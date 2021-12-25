# WindowsRemote
A Python Service To Remotely Control Your Windows From Local Network.

Ver: 1.0 beta

#### How To Install
- 1: You need `nssm` app. Download and copy it into repo directory.
- 2: Install `MainService.py` as a service. Open a terminal and type `nssm install WindowsRemote
<path_to_python> MainService.py`. Don't forget to replace `<path_to_python>` with your python installation directory.
Note that `WindowsRemote` is just a name.
- 3: Run the service, In same terminal type `nssm start WindowsRemote` and press enter. Also, you can open services
and locate `WindowsRemote` there then start it from there or set it to start automatically.


#### How To Connect
By default, The installed service on target machine will start listening at port `8085`.
You can connect to it manually or use out simple client app. To use client app first open the `client.py` file 
and change `'localhost'` to your target ip address. You can locate this by searching or in 
`Remote.__init__` method parameters.

Then just run `client.py` and you should be good to go.


#### How Does It Work
`MainService.py` starts listening at port 8085 of target machine, 
The client connects to that socket and first receives a `LOGIN;` Then it sends the password which is default to `123;`. 
After receiving `OK;` client is free to start sending commands, if a command was successful it will receive `DONE;` 
or `FAILED` on fail. Note that each command ends with a semicolon.


#### Available Commands
- `ping`: Just to see if the remote is still alive. 
- `shutdown`: Runs `shutdown /s /t 60`, This will turn off the machine after 60 seconds.
- `hibernate`: Runs `shutdown /h`, This will hibernate the machine immediately.
- `exit`: Will terminate the service. Note that the remote machine won't respond to this. 
