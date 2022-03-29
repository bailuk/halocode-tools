#!/bin/python3

"""
A mode for working with Makeblock's HaloCode devices.

Copyright (c) 2022 Lukas Bai
Copyright (c) 2015-2017 Nicholas H.Tollervey and others (see the AUTHORS file).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import time
import signal
import sys
import serial  # https://pyserial.readthedocs.io/en/latest/pyserial_api.html
import serial.tools.list_ports


debug = False
use_dsrdtr = False


class halocode_config():
    def __init__(self):
        self.COMMAND_MAX_TIME_OUT     = 10
        self.FILE_BLOCK_SIZE          = 240
        self.frame_header_str         = "F3"
        self.frame_end_str            = "F4"
        self.protocol_id_str          = "01"
        self.dev_id_str               = "00"
        self.srv_id_str               = "5E"
        self.file_header_cmd_id_str   = "01"
        self.file_block_cmd_id_str    = "02"
        self.file_delete_str          = "03"
        self.file_state_cmd_id_str    = "F0"
        self.file_type_str            = "00"

class FileTransferFSM(halocode_config):
    def __init__(self):
        super().__init__()
        self.FRAME_HEAD               = int(self.frame_header_str, 16) 
        self.FRAME_END                = int(self.frame_end_str, 16)
        self.DEV_ID                   = int(self.dev_id_str, 16)
        self.SRV_ID                   = int(self.srv_id_str, 16)
        self.CMD_STATE_ID             = int(self.file_state_cmd_id_str, 16)
        self.FTP_FSM_HEAD_S           = 0
        self.FTP_FSM_HEAD_CHECK_S     = 1
        self.FTP_FSM_LEN1_S           = 2
        self.FTP_FSM_LEN2_S           = 3
        self.FTP_FSM_DATA_S           = 4
        self.FTP_FSM_CHECK_S          = 5
        self.FTP_FSM_END_S            = 6

        self.__state = self.FTP_FSM_HEAD_S
        self.__buf = []
        self.__data_len = 0
        self.__checksum = 0x00
        self.__headchecksum = 0x00
        self.__recv_head_checksum = 0x00
        
        self.frame_received_process = None

    def get_state(self):
        return self.__state

    def set_state(self, s):
        self.__state = s

    def push_chars(self, data):
        for c in data:
            ret = self.push_char(c)
            if ret:
                if self.frame_received_process:
                    self.frame_received_process(ret)
                self.clear_buf()

    def push_char(self, c):
        if self.FTP_FSM_HEAD_S == self.__state:
            if self.FRAME_HEAD == c:
                self.__state = self.FTP_FSM_HEAD_CHECK_S
                self.__buf.clear()
                self.__checksum = 0
                self.__headchecksum = c

        elif self.FTP_FSM_HEAD_CHECK_S == self.__state:
            self.__recv_head_checksum = c
            self.__state = self.FTP_FSM_LEN1_S

        elif self.FTP_FSM_LEN1_S == self.__state:
            self.__headchecksum += c
            self.__data_len = c
            self.__state = self.FTP_FSM_LEN2_S

        elif self.FTP_FSM_LEN2_S == self.__state:
            self.__headchecksum += c
            if self.__headchecksum == self.__recv_head_checksum:
                self.__data_len += c * 256
                self.__state = self.FTP_FSM_DATA_S
            else:
                self.__state = self.FTP_FSM_HEAD_S

        elif self.FTP_FSM_DATA_S == self.__state:
            self.__checksum += c
            self.__buf.append(c)
            if len(self.__buf) == self.__data_len:
                self.__state = self.FTP_FSM_CHECK_S

        elif self.FTP_FSM_CHECK_S == self.__state:
            if (self.__checksum & 0xFF) == c:
                self.__state = self.FTP_FSM_END_S
            else:
                self.__state = self.FTP_FSM_HEAD_S
                
        elif self.FTP_FSM_END_S == self.__state:
            if self.FRAME_END == c:
                self.__state = self.FTP_FSM_HEAD_S
                return self.__buf
            else:
                self.__state = self.FTP_FSM_HEAD_S 

    def clear_buf(self):
        self.__buf.clear()

    def get_buf(self):
        return self.__buf

class file_content_parse(halocode_config):
    def __init__(self, content = ""):
        super().__init__()
        self.update(content)

    def update(self, content):
        self.content = content
        self.content_len = len(content)
        self.write_offset = 0

    def __bytes_to_hex_str(self, bytes_data):
        return " ".join("{:02x}".format(c) for c in bytes_data)

    def __calc_add_checksum(self, data):
        ret = 0
        for c in data:
            ret = ret + c
        return ret & 0xFF

    def __calc_32bit_xor(self, data):
        bytes_len = len(data)
        data_bytes = bytes(data)
        checksum = bytearray.fromhex("00 00 00 00")
        for i in range(int(bytes_len / 4)):
            checksum[0] = checksum[0] ^ data_bytes[i * 4 + 0]
            checksum[1] = checksum[1] ^ data_bytes[i * 4 + 1]
            checksum[2] = checksum[2] ^ data_bytes[i * 4 + 2]
            checksum[3] = checksum[3] ^ data_bytes[i * 4 + 3]

        if (bytes_len % 4):
            for i in range(bytes_len % 4):
                checksum[0 + i] = checksum[0 + i] ^ data_bytes[4 * int(bytes_len / 4) + i]
        return checksum

    def create_head_frame(self, target_file_path):
        # file header
        # 1(file_type) + 4(file_size) + 4(file_check_sum) = 0x09
        cmd_len_str = self.__bytes_to_hex_str((0x09 + len(target_file_path)).to_bytes(2, byteorder = 'little'))
        input_file_size_str = self.__bytes_to_hex_str(self.content_len.to_bytes(4, byteorder = 'little'))
        input_file_checksum_str = self.__bytes_to_hex_str(self.__calc_32bit_xor(self.content))
        input_file_name_str = self.__bytes_to_hex_str(bytes(target_file_path, encoding = 'utf-8'))
        frame_data_str = self.protocol_id_str + " " + self.dev_id_str + " " + self.srv_id_str + " " + \
                         self.file_header_cmd_id_str + " " + cmd_len_str + " " + self.file_type_str + " " + \
                         input_file_size_str + " " + input_file_checksum_str + " " + input_file_name_str
        frame_data_len = len(bytes.fromhex(frame_data_str))
        frame_data_len_str = self.__bytes_to_hex_str((frame_data_len).to_bytes(2, byteorder='little'))
        frame_head_checkusum_str = self.__bytes_to_hex_str(self.__calc_add_checksum(bytes.fromhex(self.frame_header_str + frame_data_len_str)).to_bytes(1, byteorder = 'little'))
        frame_checksum_str = self.__bytes_to_hex_str(self.__calc_add_checksum(bytes.fromhex(frame_data_str)).to_bytes(1, byteorder = 'little'))
        
        send_head_str = self.frame_header_str + " " + frame_head_checkusum_str + " " + frame_data_len_str + " " + \
                        frame_data_str + " " + frame_checksum_str + " " + self.frame_end_str

        return bytes.fromhex(send_head_str)
    
    def get_next_block(self):
        if self.write_offset >= self.content_len:
            return 

        if (self.write_offset + self.FILE_BLOCK_SIZE) < self.content_len:
            send_file_size = self.FILE_BLOCK_SIZE
        else:
            send_file_size = self.content_len - self.write_offset

        file_offset_str = self.__bytes_to_hex_str(self.write_offset.to_bytes(4, byteorder = 'little'))
        cmd_len_str = self.__bytes_to_hex_str((0x04 + send_file_size).to_bytes(2, byteorder = 'little'))
        file_block_str = self.__bytes_to_hex_str(bytes(self.content[self.write_offset: self.write_offset + send_file_size]))
        frame_data_str = self.protocol_id_str + " " + self.dev_id_str + " " + self.srv_id_str + " " + self.file_block_cmd_id_str + \
                         " " + cmd_len_str + " " + file_offset_str + " " + file_block_str
        frame_data_len = len(bytes.fromhex(frame_data_str))
        frame_data_len_str = self.__bytes_to_hex_str((frame_data_len).to_bytes(2, byteorder = 'little'))
        frame_head_checkusum_str = self.__bytes_to_hex_str(self.__calc_add_checksum(bytes.fromhex(self.frame_header_str + frame_data_len_str)).to_bytes(1, byteorder = 'little'))
        frame_checksum_str = self.__bytes_to_hex_str(self.__calc_add_checksum(bytes.fromhex(frame_data_str)).to_bytes(1, byteorder = 'little'))

        send_block_str = self.frame_header_str + " " + frame_head_checkusum_str + " " + frame_data_len_str + \
                         " " + frame_data_str + " " + frame_checksum_str + " " + self.frame_end_str

        send_block_bytes = bytearray.fromhex(send_block_str)

        self.write_offset += send_file_size
        
        return send_block_bytes
    
    def get_current_percentage(self):
        return int(100 * self.write_offset / self.content_len)

class halocode_communication():
    def __init__(self):
        self.serial_fd = None
        self.input_file_content = None
        self.target_file_path = None

        self.ftp_process = FileTransferFSM()
        self.ftp_process.frame_received_process = self.__frame_process
        self.file_content = file_content_parse()

        self.process_status = 0

    def update_paras(self, serial, content, target_file_path):
        self.serial_fd = serial
        self.input_file_content = content
        self.target_file_path = target_file_path
        self.file_content.update(content)
        self.process_status = 0
        
    def send_file_content(self, ser = None, input_file_data = None, target_file_path = None):
        if ser == None:
            ser = self.serial_fd
        if input_file_data == None:
            input_file_data = self.input_file_content
        if target_file_path == None:
            target_file_path = self.target_file_path
       

        if self.process_status == 0:
            frame = self.file_content.create_head_frame(self.target_file_path)
            if frame:
               if debug: print(f'write frame: ${frame}')
               ser.write(frame)
               self.process_status = 1
        else:
            frame = self.file_content.get_next_block()
            
            if frame:
                if debug: print(f'write frame: ${frame}')
                ser.write(frame)
                self.show_status_message("transmitting: %s%s" %('%', self.file_content.get_current_percentage(), ))

    def __frame_process(self, frame):
        if (0x01 == frame[0] and 0x00 == frame[6]):
            if self.file_content.get_current_percentage() < 100:
                self.send_file_content()
            else:
                global uploading
                uploading = False
                self.show_status_message("Complete file transfer!")
                self.process_status = 0


    def show_status_message(self, message):
        print(message)


def find_port(vid=6790, pid=29987):
    """
    Find the port of Makeblock's devices
    Return: Makeblock Device or None if not found
    """
    for port in serial.tools.list_ports.comports():
        if port.vid == vid and port.pid == pid:
            return port.device
    return None


def file_read(path):
    file = open(path, 'r')
    data = file.read()
    file.close()
    return data

def init_upload(path, ser):
    target_path = '/flash/main.py'
    script = file_read(path).encode('utf-8')
    print(f'uploading {path} to {target_path}')

    comm = halocode_communication()
    comm.update_paras(ser, script, target_path)
    comm.send_file_content()
    return comm


def upload_and_log(path = ''):
    """
    Upload Code to Makeblock Devices
    """

    global uploading
    uploading = path != ''

    port = find_port()

    if port == None:
        print('Could not find an attached Makeblock Device')
        print('Please attach your Makeblock device (Codey Rocky or HaloCode) with USB Cable')

    else:
        print(f'Connecting to {port}')
        ser = serial.Serial(port, 115200, dsrdtr=use_dsrdtr)

        if uploading:
            comm = init_upload(path, ser)

        print('press Ctrl+C to cancel')

        global running
        while running:
            if ser.in_waiting > 0 and ser.out_waiting == 0:
                if debug: print('input received')
                
                bytes = ser.read_all()
                if uploading: comm.ftp_process.push_chars(bytes)
                try:
                    sys.stdout.write(bytes.decode())
                except:
                    pass

            time.sleep(0.25)


running = True
uploading = False


def signal_handler(signal, frame):
    global running
    running = False


signal.signal(signal.SIGINT, signal_handler)


if len(sys.argv) < 2:
    print('No file specified. Connecting to log console')
    upload_and_log()

else:
    upload_and_log(sys.argv[1])
