FROM python3
COPY . /prayers-and-readings
WORKDIR /prayers-and-readings
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt
