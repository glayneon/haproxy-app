import streamlit as st
import streamlit_authenticator as stauth

# from loguru import logger
from enum import Enum
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
import subprocess
import re


# Constants
class Config(Enum):
    TEST_CLUSTER_LB = "etc/haproxy/cluster-lb.cfg"
    TEST_WORKER_LB = "etc/haproxy/worker-lb.cfg"
    CLUSTER_LB = "/etc/haproxy/cluster-lb.cfg"
    CLUSTER_9345 = 9345
    CLUSTER_6443 = 6443
    WORKER_LB = "/etc/haproxy/worker-lb.cfg"
    WORKER_80 = 80
    WORKER_443 = 443
    WORKER_30000 = 30000
    WORKER_30001 = 30001


# variables
TEST_LB_CONFIG = {
    "LB_CLUSTER": Config.TEST_CLUSTER_LB.value,
    "LB_CLUSTER_PORTS": [
        Config.CLUSTER_9345.value,
        Config.CLUSTER_6443.value,
    ],
    "LB_WORKER": Config.TEST_WORKER_LB.value,
    "LB_WORKER_PORTS": [
        Config.WORKER_80.value,
        Config.WORKER_443.value,
        Config.WORKER_30000.value,
        Config.WORKER_30001.value,
    ],
}

REAL_LB_CONFIG = {
    "LB_CLUSTER": Config.CLUSTER_LB.value,
    "LB_CLUSTER_PORTS": [
        Config.CLUSTER_9345.value,
        Config.CLUSTER_6443.value,
    ],
    "LB_WORKER": Config.WORKER_LB.value,
    "LB_WORKER_PORTS": [
        Config.WORKER_80.value,
        Config.WORKER_443.value,
        Config.WORKER_30000.value,
        Config.WORKER_30001.value,
    ],
}


def show_lb_cfg(filename):
    _file = Path(filename)

    try:
        if _file.exists:
            with st.expander(f"HAProxy {_file.name} Config"):
                st.text_area(
                    _file.name,
                    value=_file.read_text(encoding="utf-8"),
                    height=300,
                )
            st.session_state.cfg_file = True
    except FileNotFoundError:
        st.error(f"{filename} is not Found..")
        st.session_state.cfg_file = False


def write_backend_cfg(filename, ports, how_many):
    _file = Path(filename)
    service_ports = ports
    _print_name = _file.name.split("-")[0]
    new_config = ""
    for service_port in service_ports:
        new_config += f"""
backend rke2-{service_port}-api
    mode tcp
    option tcplog
    option tcp-check
    balance roundrobin
    default-server inter 10s downinter 5s rise 2 fall 2 slowstart 60s maxconn 250 maxqueue 256 weight 100
"""
        for k in range(1, how_many + 1):
            new_config += f"""    server {st.session_state[_print_name+str(k)]} {st.session_state[_print_name+'_ip'+str(k)]}:{service_port} check
"""

    if _file.exists:
        _file.write_text(new_config, encoding="utf-8")
        st.success(f"New HAProxy Back-End config is saved: {_file.name}")


def ip_checker(ip):
    ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    check = re.match(ip_pattern, str(ip))

    if check:
        return True
    else:
        return False


def haproxy_restart():
    subprocess.run(["systemctl restart haproxy"], shell=True)
    rt_status = subprocess.run(
        ["systemctl status haproxy --no-pager"],
        shell=True,
        capture_output=True,
    )

    return rt_status.stdout.decode("utf-8")


def haproxy_config(filename, ports, how_many):
    _print_name = filename.name.split("-")[0]

    if all(
        f"{_print_name}{key}" in st.session_state.keys()
        for key in range(1, how_many + 1)
    ) and all(
        f"{_print_name}_ip{key}" in st.session_state.keys()
        for key in range(1, how_many + 1)
    ):
        if all(
            ip_checker(st.session_state[f"{_print_name}_ip{str(key)}"])
            for key in range(1, how_many + 1)
        ):
            write_backend_cfg(filename, ports, how_many)


def show_ip_input(filename, ports, keyname):
    _file = Path(filename)
    _print_name = _file.name.split("-")[0]
    str_ports = "/".join([str(x) for x in ports])
    how_many = st.slider("Master Nodes", 1, 10, 1, key=f"{keyname}_many")
    aaa = st.button("OK", key=f"{keyname}_ok")
    if how_many and aaa:
        with st.form(f"{_print_name}_form1"):
            st.subheader(f"{_print_name.title()} Nodes Ports ({str_ports})")
            col1, col2 = st.columns(2)
            with col1:
                for i in range(1, how_many + 1):
                    st.text_input(
                        f"{_print_name} Hostname {i}",
                        max_chars=20,
                        key=f"{_print_name}{i}",
                    )
            with col2:
                for i in range(1, how_many + 1):
                    st.text_input(
                        f"{_print_name} IP {i}",
                        max_chars=15,
                        key=f"{_print_name}_ip{i}",
                    )

            if st.form_submit_button(
                "Submit",
                on_click=haproxy_config,
                args=(_file, ports, how_many),
            ):
                # show_lb_cfg(haproxy_path)
                if result := haproxy_restart():
                    with st.expander("HAProxy Restart"):
                        st.text_area(
                            "HAProxy Status Log", value=result, height=300
                        )


if __name__ == "__main__":
    # Open YAML file
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Create authenticator object
    with st.sidebar:
        authenticator = stauth.Authenticate(
            config["credentials"],
            config["cookie"]["name"],
            config["cookie"]["key"],
            config["cookie"]["expiry_days"],
            auto_hash=False,
        )

        # Render the login widget
        authenticator.login("sidebar", 5, 5, captcha=False, key="login1")

        # hasehd_pwd = stauth.Hasher([]).generate()
        # st.write(hasehd_pwd)

    # Authenticate users
    if st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")
    elif st.session_state["authentication_status"] is None:
        st.warning("Please enter your username and password")

    elif st.session_state["authentication_status"]:
        with st.sidebar:
            authenticator.logout()
            st.write(f'# Welcome *{st.session_state["name"]}*')
            "HAProxy App 은 HAProxy 의 Backend Config 의 수정 및 재시작을 제공 합니다."
            "Backend Config 에는 다음 포트가 등록되어 있습니다"
            " 9345 / 6443 / 80 / 443 / 30000 / 30001  "
            "[View the source code](https://github.com/kubeops2/lb2/blob/main/haproxy_web/haproxy_web.py)"

        st.title("HAProxy App")
        # masters
        show_lb_cfg(TEST_LB_CONFIG["LB_CLUSTER"])
        show_lb_cfg(TEST_LB_CONFIG["LB_WORKER"])
        if st.session_state.cfg_file is True:
            show_ip_input(
                TEST_LB_CONFIG["LB_CLUSTER"],
                TEST_LB_CONFIG["LB_CLUSTER_PORTS"],
                "master",
            )
            show_ip_input(
                TEST_LB_CONFIG["LB_WORKER"],
                TEST_LB_CONFIG["LB_WORKER_PORTS"],
                "worker",
            )
