# استفاده از تصویر رسمی پایتون به عنوان base image
FROM python:3.11-slim

# تنظیم مسیر کاری
WORKDIR /workspace

# نصب پیش‌نیازها
RUN apt-get update && apt-get install -y git

# نصب poetry
RUN pip install poetry

CMD ["bash"]