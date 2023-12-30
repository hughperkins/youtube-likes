"""
- Ensure that config.yml has valid google_client_id and google_client_secret
- Run this
- open http://localhost:8080
- Click through the prompts
=> refresh token will be saved in your config.yml
"""
from typing import Optional
import aiohttp.web
import argparse
from ruamel.yaml import YAML


yaml = YAML()
config: Optional[dict[str, str]] = None


async def root(request: aiohttp.web.Request):
    global config
    assert config is not None
    print(request)
    print(request.query_string)
    code = request.rel_url.query.get('code', None)
    if code is not None:
        print('code', code)
        config['google_refresh_token'] = code
        with open(args.config_filepath, 'w') as f:
            yaml.dump(config, f)
        return aiohttp.web.Response(text=f"<html><body>code is<br>{code}</body></html>", content_type="text/html")
    else:
        with open('html/index.html') as f:
            jinja_template = f.read()
        jinja_template = jinja_template.replace('{{client_id}}', config["google_client_id"]).replace(
            "{{client_secret}}", config['google_client_secret']
        )
        return aiohttp.web.Response(text=jinja_template, content_type="text/html")


def run(args: argparse.Namespace) -> None:
    global config

    with open(args.config_filepath) as f:
        config = yaml.load(f)
    app = aiohttp.web.Application()
    app.add_routes([aiohttp.web.get('/', root)])
    app.router.add_static('/html/', path='html', name='html')
    aiohttp.web.run_app(app)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-filepath", type=str, default="config.yml")
    args = parser.parse_args()
    run(args)
