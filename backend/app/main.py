from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import invoice_router

app = FastAPI(title="Smart Invoice Pro API", version="1.0")

# 解决 CORS 跨域问题的核心配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有前端地址访问（测试环境推荐）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有请求方法(POST, GET等)
    allow_headers=["*"],  # 允许所有请求头
)

# 注册路由
app.include_router(invoice_router.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)