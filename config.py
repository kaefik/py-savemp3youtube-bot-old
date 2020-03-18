""" Хранение настроек приложения """

import os
import csv
import configparser

class Config:
    
    def __init__(self,namefile_cfg = "config.ini"):
        self.namefile_cfg = namefile_cfg
        self.token=None
        if not os.path.exists(self.namefile_cfg):
            return
        config = configparser.ConfigParser()
        config.read(self.namefile_cfg)
        self.token = str(config['BOT']['token'])
        # список пользователей        
        self.admin = {"username": str(config['ADMIN']['username']),
            "id": int(config['ADMIN']['userid'])}
        # TODO: сделать загрузку пользователей которые имеют доступ к боту
        self.allow_users =[]
        self.allow_users.append(self.admin)
        

if __name__ == "__main__":
    cfg = Config("config.ini")
    print(cfg.token)
    print(cfg.admin)
    print(cfg.allow_users)