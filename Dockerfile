# 以python3.7为基础镜像构建
FROM python:3.7
# 安装nginx与supervisor
RUN apt-get update && apt-get install -y nginx supervisor
# 安装gevent与gunicorn
RUN pip install gevent gunicorn
# 解决输出可能的中文乱码
ENV PYTHONIOENCODING=utf-8

# 创建并设置工作目录
WORKDIR /project/flaskai
# 拷贝包文件到工作目录
COPY requirements.txt /project/flaskai
# 安装包
RUN pip install -r requirements.txt

# nginx配置相关
# 删除默认的有效配置，sites-enabled 目录下的配置文件才能够真正被用户访问
RUN rm /etc/nginx/sites-enabled/default
# 复制配置文件到sites-available目录
COPY nginx.conf /etc/nginx/sites-available/
# 将配置文件链接到sites-available目录
RUN ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/nginx.conf
# 添加自定义CMD时,添加此命令到nginx全局配置中保证容器可以跟踪到进程，防止容器退出
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

# supervisord配置相关
RUN mkdir -p /var/log/supervisor
# 使用自定义supervisor配置替换默认配置
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
# 使用自定义gunicorn配置替换默认配置
COPY gunicorn.conf /etc/supervisor/conf.d/gunicorn.conf
# 指定容器运行启动命令
CMD ["/bin/bash"]