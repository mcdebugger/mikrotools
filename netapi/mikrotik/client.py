import paramiko

class MikrotikSSHClient():
    def __init__(self, host: str, username: str, password: str = None, keyfile: str = None, port: int = 22):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._keyfile = keyfile
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._connected = False
    
    def connect(self) -> None:
        disabled_algorithms = {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}
        timeout = 5
        
        # Check if password or keyfile is provided
        if self._password is not None and self._keyfile == None:
            # Connect with password
            try:
                self._ssh.connect(
                    self._host,
                    port=self._port,
                    username=self._username,
                    password=self._password,
                    disabled_algorithms=disabled_algorithms,
                    timeout=timeout,
                    look_for_keys=False
                )
                self._connected = True
            except Exception as e:
                raise e
        elif self._keyfile is not None and self._password == None:
            # Connect with key
            try:
                self._ssh.connect(
                    self._host,
                    port=self._port,
                    username=self._username,
                    key_filename=self._keyfile,
                    disabled_algorithms=disabled_algorithms,
                    timeout=timeout,
                    look_for_keys=False
                )
                self._connected = True
            except Exception as e:
                raise e
        else:
            raise Exception('Must provide either password or keyfile')
    
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
        return self.execute_command_raw(f':put [{path}]').strip()
    
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
        
    def get_identity(self) -> str:
        """
        Retrieves the identity of the router.

        Returns:
            The identity of the router as a string.
        """
        return self.get('/system identity', 'name')
    
    def get_routeros_installed_version(self) -> str:
        """
        Retrieves the currently installed version of RouterOS.

        Returns:
            The installed version of RouterOS as a string.
        """
        return self.get('/system package update', 'installed-version')

    def get_current_firmware_version(self) -> str:
        """
        Retrieves the current firmware version of the router.

        Returns:
            The current firmware version as a string.
        """
        return self.get('/system routerboard', 'current-firmware')
    
    def get_upgrade_firmware_version(self) -> str:
        """
        Retrieves the upgrade firmware version of the router.

        Returns:
            The upgrade firmware version as a string.
        """
        return self.get('/system routerboard', 'upgrade-firmware')
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
