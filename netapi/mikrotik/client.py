import paramiko

class MikrotikSSHClient():
    def __init__(self, host: str, username: str, keyfile: str, port: int = 22):
        self.host = host
        self.port = port
        self.username = username
        self.keyfile = keyfile
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._connected = False
    
    def connect(self) -> None:
        try:
            self._ssh.connect(
                self.host,
                port=self.port,
                username=self.username, 
                key_filename=self.keyfile,
                timeout=5
            )
            self._connected = True
        except Exception as e:
            raise e
    
    def disconnect(self) -> None:
        if self._connected:
            self._ssh.close()
            self._connected = False
    
    def execute_command(self, command: str) -> list[str]:
        """
        Execute a command on the Mikrotik device and return its output as a list of strings.

        :param command: The command to execute
        :return: The output of the command
        :raises: ConnectionError if not connected to the host
                 RuntimeError if the command execution fails
        """
        output = self.execute_command_raw(command).strip().split('\n')
        
        return [line.strip() for line in output if line.strip()]
    
    def execute_command_raw(self, command: str) -> str:
        """
        Execute a command on the Mikrotik device and return its output as a raw string.

        :param command: The command to execute
        :return: The output of the command
        :raises: ConnectionError if not connected to the host
                 RuntimeError if the command execution fails
        """
        if not self._connected:
            raise ConnectionError('Not connected to host')
        
        try:
            _, stdout, stderr = self._ssh.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode().strip()
            
            if error:
                raise RuntimeError(f'Error executing command: {error}')
            
            return output
        except paramiko.SSHException as e:
            raise e
    
    def get(self, path: str, obj: str = None) -> str:
        """
        Retrieves an object from a path on the router.

        Args:
            path: The path to the object
            obj: The object to retrieve

        Returns:
            The value of the object as a string
        """
        # Remove trailing slash
        path = path.rstrip('/')
        
        if obj:
            path = f'{path} get {obj}'
        else:
            path = f'{path} get'
        return self.execute_command(f':put [{path}]')[0]
    
    def get_dict(self, path: str, obj: str = None) -> list[str]:
        """
        Retrieves a dictionary representation of an object's properties from a path on the router.

        Args:
            path: The path to the object.
            obj: The object to retrieve. Optional, if not specified, retrieves default object.

        Returns:
            A dictionary where keys are the object's property names and values are the corresponding
            property values, extracted from the response string.
        """
        output = {}
        current_key = None
        
        response = self.get(path, obj)
        
        for part in response.split(';'):
            part = part.strip()
            if not part:
                continue
            
            if '=' in part:
                key, value = part.split('=', 1)
                current_key = key.strip()
                output[current_key] = value.strip()
            elif current_key and current_key in output:
                output[current_key] += ';' + part.strip()
        
        return output
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
