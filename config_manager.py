import configparser

class ConfigManager:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.conf=[]
        for categories,conf in self.config.items():
          if categories == "DEFAULT" :
            continue
          sheet_name = conf['nomdelafeuille']
          sheet_tab = conf['onglet']
          columns = conf['liste'].split(',')
          share_emails = [email.strip() for email in conf['emails'].split(',')]
          self.conf.append({
            'sheet_name': [sheet_name],
            'sheet_tab': sheet_tab,
            'columns': columns,
            'share_emails': share_emails
          })
      

    def get_config(self):
      
      return self.conf
 

