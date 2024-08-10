default: run

app := "src.main"

alias i := install
alias l := lint

set positional-arguments

# 安装依赖
install:
    uv pip install -r requirements.dev.txt
    pre-commit install --install-hooks

# 统一代码风格
lint:
    ruff check --fix .
    ruff format .

# # 生成数据库变更记录
# makemigration message:
#     alembic revision --autogenerate -m $1

# # 执行数据库变更记录
# migrate revision:
#     alembic upgrade $1

# # 降级数据库变更记录
# downgrade revision:
#     alembic downgrade $1

# # 运行本地依赖
# local:
#     docker compose -f compose.local.yaml up -d

# 运行开发服务器
run:
    python -m {{app}}

# # 运行生产服务器
# start: config
#     gunicorn -k uvicorn.workers.UvicornWorker {{app}}

# # 检查生产服务器配置
# config:
#     gunicorn --print-config {{app}}

# # 部署
# deploy *docker-compose-args='':
#     docker compose up $@
