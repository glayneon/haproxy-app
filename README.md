# Haproxy-App 

<br>

HAproxy-App 은 k8s 멀티 마스터 및 워커 구성 시 필요한 LoadBalancer 환경을 쉽게 구성하기 위해 만들어진 `StreamLit` 기반 앱이다.
이 앱은 haproxy 를 다음과 같이 제어할 수 있는 환경을 제공한다.

<br>

* Master Node LoadBalancing
    * 기본 Master LB 설정 파일 : `cluster-lb.cfg`
        * 없으면, 앱으로 설정시 자동 생성함.
    * 기본 Load Balancing Ports
        * TCP 9345 - Rancher Kubernetes Cluster 구성 시 Master Node 가 Cluster 에 조인 시 통신을 위한 포트
        * TCP 6443 - K8s API Server Port

    * 기본 Worker LB 설정 파일 : `worker-lb.cfg`
        * 없으면, 앱으로 설정시 자동 생성함.
    * 기본 Load Balancing Ports
        * TCP 80 - HTTP
        * TCP 443 - HTTPS
        * TCP 30000-30001 - 기본 Node Port 중 두 개 고정

<br> 

> [StreamLit 이 궁금하다면 클릭 ](https://streamlit.io/)

<br>

## Requirements

<br>

이 앱이 구동되는 컨테이너 또는 호스트는 다음 사항이 구성되어 있어야 한다.

- haproxy 설치
- config 폴더 위치가 `/etc/haproxy/` 로 되어 있어야 한다.
- 이 앱이 haproxy 를 start/stop 할 수 있는 권한이 있어야 한다.
- config.yaml 이 구성되어 있어야 한다.
    - config.yaml 에 계정선언 및 패스워드 HASH 가 필요함.

<br>

> 주의!!
> 현재는 `subprocess` 모듈로 `systemctl` 을 이용하여 `haproxy` 를 제어하도록 구성되어 있으며, 리눅스 배포본이 달라지면, 달라진 서비스 제어에 맞게 변경되어야 한다.

<br>

## 환경 구성 및 구동하기

<br>

1. git clone

```bash
$ git clone https://github.com/glayneon/haproxy-app.git

```
<br>

2. venv 로 환경 구성

```bash
$ python -m venv haproxy-app

```

<br>

3. pip 으로 필수 패키지 설치

```
$ source haproxy-app/bin/activate
...

$ pip install --upgrade pip
...

$ cd haproxy-app && pip install -r ./requirements.txt
...
...
```

<br>

4. 구동하여 확인

```bash
$ streamlit run haproxy-app
...
```

<br>

백그라운드 구동 시
```bash
$ nohup streamlit run haproxy-app &
...
...
```

