# murakami-plot

murakami-plot is designed to visualize the output from the M-Lab
[murakami](https://github.com/m-lab/murakami) output.

```
docker run -d --restart always --name murakami-plot \
    -v $PWD/share:/share -p 8000:8000 \
    soltesz/murakami-plot:v0.1 /scatter.py /share/history.csv
```
