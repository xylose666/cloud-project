name: CI/CD Pipeline
on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build and Push Image
        run: |
          IMAGE_TAG=${{ github.sha }}
          # 登录华为云 SWR
          echo ${{ secrets.SWR_PWD }} | docker login -u ${{ secrets.SWR_USER }} --password-stdin swr.cn-north-4.myhuaweicloud.com
          # 构建镜像
          docker build -t swr.cn-north-4.myhuaweicloud.com/cloud2576/backend:$IMAGE_TAG ./backend
          # 推送镜像
          docker push swr.cn-north-4.myhuaweicloud.com/cloud2576/backend:$IMAGE_TAG

      - name: Deploy to K8s
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.K8S_HOST }}
          username: ${{ secrets.K8S_USER }}
          key: ${{ secrets.K8S_SSH_KEY }}
          script: |
            # 使用最新的 Tag 更新 Kubernetes 部署
            kubectl set image deployment/backend-deployment backend=swr.cn-north-4.myhuaweicloud.com/cloud2576/backend:${{ github.sha }} -n default