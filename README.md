# murakami-plot


```
docker run -d --restart always --name murakami-plot \
    -v $PWD/share:/share -p 8000:8000 \
    soltesz/murakami-plot:v0.1 /scatter.py /share/history.csv
```
