"""Точка входа для запуска (flask run / gunicorn / production)."""
import os
import re

from app import create_app

app = create_app()


class UrlPrefixRewriter:
    """Префиксирует все абсолютные ссылки в HTML/CSS ответах (для деплоя на pplx.app).

    Обратный прокси срезает префикс (например /port/5000) из PATH_INFO,
    поэтому Flask url_for выдаёт «голые» пути. Но в браузере эти пути
    нужны с префиксом. Переписываем ответ на лету.
    """

    HTML_PATTERNS = [
        # href="/...", src="/...", action="/..." — но не "//" (протокол-относительные)
        # Один слэш или слэш + путь, но не //
        re.compile(rb'(href|src|action)="(/(?![/])[^"]*)"'),
        re.compile(rb"(href|src|action)='(/(?![/])[^']*)'"),
    ]

    def __init__(self, wsgi_app, prefix: str):
        self.wsgi_app = wsgi_app
        self.prefix = prefix.rstrip("/").encode()

    def __call__(self, environ, start_response):
        captured = {}

        def _start_response(status, headers, exc_info=None):
            # Перепишем Location в редиректах
            new_headers = []
            for k, v in headers:
                if k.lower() == "location" and v.startswith("/") and not v.startswith("//"):
                    v = self.prefix.decode() + v
                new_headers.append((k, v))
            captured["status"] = status
            captured["headers"] = new_headers
            return start_response(status, new_headers, exc_info)

        chunks = list(self.wsgi_app(environ, _start_response))
        body = b"".join(chunks)

        ct = next((v for k, v in captured.get("headers", []) if k.lower() == "content-type"), "")
        if "text/html" in ct or "application/xhtml" in ct:
            for pat in self.HTML_PATTERNS:
                body = pat.sub(
                    lambda m: m.group(1) + b'="' + self.prefix + m.group(2) + b'"',
                    body,
                )
            # Обновим Content-Length в заголовках
            headers = [
                (k, str(len(body)) if k.lower() == "content-length" else v)
                for k, v in captured["headers"]
            ]
            captured["headers"][:] = headers

        return [body]


prefix = os.environ.get("URL_PREFIX", "").strip()
if prefix:
    app.wsgi_app = UrlPrefixRewriter(app.wsgi_app, prefix)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
