# murakami-plot

murakami-plot is designed to visualize the output from the M-Lab
[murakami](https://github.com/m-lab/murakami).

murakami-plot generates three plots by default.

 * 250ms instantaneous rate vs time for the 10 seconds of the test.
 * average rate vs time for 24 hours, to highlight diurnal patterns over time.
 * average rate vs time, for a simple time series.

```
docker run -d --restart always --name murakami-plot \
    -v $PWD/data:/data -v $PWD/share:/share -p 8000:8000 \
    soltesz/murakami-plot:v0.3 /scatter.py /share/history.csv
```
