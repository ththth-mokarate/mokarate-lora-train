FROM pytorch/pytorch:2.9.1-cuda12.8-cudnn9-runtime

RUN apt-get update && apt-get install -y --no-install-recommends git curl libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN git clone https://github.com/ostris/ai-toolkit.git /app/ai-toolkit
WORKDIR /app/ai-toolkit
RUN pip install --no-cache-dir -r requirements.txt

COPY dataset/ /app/dataset/
COPY mokarate_face_v1.yml /app/mokarate_face_v1.yml
COPY server.py /app/server.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 3000
CMD ["/app/entrypoint.sh"]
