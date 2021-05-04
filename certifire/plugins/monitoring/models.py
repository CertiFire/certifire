import json

import certifire.config as config
from certifire import database, db
from certifire.plugins.dns_providers.route53 import Route53Dns
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship


class Target(db.Model):
    __tablename__ = "mon_targets"
    id = Column(Integer, primary_key=True)
    ip = Column(String(32))
    host = Column(Text())
    url = Column(Text())
    bw_url = Column(Text())

    worker = relationship("Worker", foreign_keys="Worker.mon_target")

    def __init__(self, ip=None, host=None, url=None, bw_url=None):
        self.ip = ip
        self.host = host
        self.url = url
        self.bw_url = bw_url

    def create(self):
        if not self.ip and not self.host:
            return False, -1
        if not self.url:
            if self.host:
                self.url = "http://"+self.host
            else:
                self.url = "http://"+self.ip

        try:
            database.create(self)
            return True, self.id
        except:
            return False, -1
    
    def delete(self):
        try:
            database.delete(self)
            return True
        except:
            return False

    def __repr__(self):
        return "Target(label={label})".format(label=self.id)

    @property
    def json(self):
        return json.dumps({
            'id': self.id,
            'ip': self.ip,
            'host': self.host,
            'url': self.url,
            'bw_url': self.bw_url,
        }, indent=4)


class Worker(db.Model):
    __tablename__ = "mon_workers"
    id = Column(Integer, primary_key=True)
    ip = Column(String(32))
    host = Column(Text())
    location = Column(Text())
    mon_self = Column(Boolean())
    mon_target = Column(Integer, ForeignKey("mon_targets.id"))

    def __init__(self, ip=None, host=None, location=None, mon_self=False, mon_url=None, bw_url=None):
        self.ip = ip
        self.host = host
        self.location = location
        self.mon_self = mon_self
        self.bw_url = bw_url
        self.mon_url = mon_url

    def create(self, create_host=False):
        try:
            database.create(self)
            
            if not self.host and create_host and self.ip:
                r53 = Route53Dns()
                host = "w{}.".format(self.id)+config.MON_BASE_URL
                r53.create_a_record(host, self.ip)
                self.host = host
                database.update(self)
            
            if self.mon_self:
                T = Target(self.ip, self.host, self.mon_url, self.bw_url)
                status = T.create()
                if status:
                    self.mon_target = T.id
                    database.update(self)
                    return True
                else:
                    return False
            return True
        except:
            return False
    
    def delete(self):
        try:
            database.delete(self)
            if self.mon_self:
                T = Target.query.get(self.mon_target)
                return T.delete()
            return True
        except:
            return False

    
    def __repr__(self):
        return "Target(label={label})".format(label=self.id)

    @property
    def json(self):
        return json.dumps({
            'id': self.id,
            'ip': self.ip,
            'host': self.host,
            'location': self.location,
            'mon_self': self.mon_self,
            'mon_target': self.mon_target
        }, indent=4)
