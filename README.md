### plamd
##### ping probe microservice <br />
<a><img src="https://raw.githubusercontent.com/darzanebor/plamd/master/img/result.png" title="pylint"></a>

##### docker
###
```
docker run -d \
  --sysctl 'net.ipv4.ping_group_range=101 101' \
  -p 5000:5000 \
  alphaceti/plamd:cbc5b16c
```
```
curl 'localhost:5000/ip.ping/?target=aol.com&count=9&interval=0.1'
```
