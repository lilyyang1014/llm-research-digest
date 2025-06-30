# (可以放在一个临时文件如 create_db.py 中运行一次)
from database import engine, Base
from models import Paper, Institution # 确保所有模型都被导入

print("Creating database and tables...")
Base.metadata.create_all(bind=engine)
print("Database and tables created successfully.")