# Simple Tweeter Server Handles Multi-Clients

> Allows multi-clients connects to server, subscribe and tweets message with hashtags

[![Build Status](http://img.shields.io/travis/badges/badgerbadgerbadger.svg?style=flat-square)](https://travis-ci.org/badges/badgerbadgerbadger) [![Dependency Status](http://img.shields.io/gemnasium/badges/badgerbadgerbadger.svg?style=flat-square)](https://gemnasium.com/badges/badgerbadgerbadger)

## Table of Contents

- [Installation](#installation)
- [Features](#features)
- [Usages](#usages)
- [Contributing](#contributing)
- [Team](#team)
- [Support](#support)
- [License](#license)

---

## Installation

- Require `Python >= 3.6 Version`
- Download or git clone the project

### Clone

- Clone this repo to your local machine using `https://github.com/nhat-lan/networking.git`

### Setup

> update and install this Python 3 version

```shell
$ brew update && upgrade
$ brew install python3
```

---

## Features

Users can send tweet with one or multiple hashtags, get all messages receive from server (messages related to hashtags that user subscribed to), retrieve online users list, subscribe hashtag, unsubscribe hashtag.

---
## Usages

Move to the top directory of the project.

Running Server:
```python3
$ python3 ttweetser.py <portnumber>

```

Running Clients:
```python3
$ python3 ttweetcli.py <serverip> <portnumber> <username>

```


Client can use commands such as `tweet, subscribe, unsubscribe, timeline, getusers, exit`.

- `tweet "<message>" <hashtag>`

```python3
$ tweet "Here is my mesage" #myhashtag1
$ tweet "Here is my mesage" #myhashtag#anotherHashTag
```

- `subscribe <hashtag>`

```python3
$ subscribe #myhashtag1
$ subscribe #ALL
```

- `unsubscribe <hashtag>`

```python3
$ unsubscribe #myhashtag1
$ unsubscribe #ALL
```

- `timeline`

```python3
$ timeline
```

- `getusers`

```python3
$ getusers
```

- `exit`

```python3
$ exit
```

```
Note:
  - Server IP: `0.0.0.0` or `127.0.0.1`
  - Message format:
    + Message is always between `""`, within range [1,150] characters
  - Hashtag format:
    + Hashtag is within range [1,] not included `#`, can only included alphanumeric characters ([a-zA-Z0-9])
    + Hashtag #ALL is reserved, so client cannot tweet with this hashtag
  - Username format:
    + Can only included alphanumeric characters ([a-zA-Z0-9])
  - Subscribe:
    + Client can only subscribe one hashtag at a time
    + Clients can only subscribe up to 3 hashtag (unless unsubscribe previous subscribed hashtags)
  - Client will be removed from server when exiting. Server only store active clients.
```

---

## Contributing

> To get started...

### Step 1

- **Option 1**
    - 🍴 Fork this repo!

- **Option 2**
    - 👯 Clone this repo to your local machine using `https://github.com/nhat-lan/networking.git`

### Step 2

- **HACK AWAY!** 🔨🔨🔨

### Step 3

- 🔃 Create a new pull request using <a href="`https://github.com/nhat-lan/networking/compare/" target="_blank">`https://github.com/nhat-lan/networking/compare/`</a>.

---

## Team
[1.1]:https://github.com/nhat-lan
[1.2]:https://www.linkedin.com/in/lan-letu/
[1.3]:mailto:lan.letu@gatech.edu
[2.1]:https://github.com/uyendinhh
[2.2]:https://www.linkedin.com/in/uyen-dinhh/
[2.3]:mailto:udinh3@gatech.edu
[3.1]:https://github.com/kiettran95
[3.2]:https://www.linkedin.com/in/kiet-tran95/
[3.3]:mailto:ktran86@gatech.edu

- `Nhat Lan Le Tu`

[![github](https://img.icons8.com/nolan/64/github.png)][1.1][![linkedin](https://img.icons8.com/nolan/64/linkedin.png)][1.2][![email](https://img.icons8.com/nolan/64/email.png)][1.3]

- `Uyen Dinh`

[![github](https://img.icons8.com/nolan/64/github.png)][2.1][![linkedin](https://img.icons8.com/nolan/64/linkedin.png)][2.2][![email](https://img.icons8.com/nolan/64/email.png)][2.3]

- `Kiet Tran`

[![github](https://img.icons8.com/nolan/64/github.png)][3.1][![linkedin](https://img.icons8.com/nolan/64/linkedin.png)][3.2][![email](https://img.icons8.com/nolan/64/email.png)][3.3]


---

## Support

Please reach out to our team!


---

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)