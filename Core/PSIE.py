def calc(t,d,a):
    J=t*100+d*10
    SDI=d/(t+1) if t else 1
    SDI=max(0,min(1,SDI))
    A=max(0,min(1,a))
    return J,SDI,A
