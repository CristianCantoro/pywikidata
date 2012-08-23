# -*- coding: utf-8 -*-

from request import RequestHandler
from item import Item
import errors

import json

""" Internal API class. Use api object instead. """
class _API:
    def __init__(self, config):
        self.request = RequestHandler(config)
        self.config = config

    def getItemsById(self, ids=[]):
        ids = [str(x) for x in ids]
        resp = self.request.get({"action":"wbgetitems", "ids": "|".join(ids)})
        items = self._createItemCollection(resp["items"])
        return items

    def getItemById(self, iid):
        return self.getItemsById([iid])[0]

    def getItemsByInterwikis(self, sites=[], titles=[]):
        pass

    def getItemByInterwiki(self, site, title):
        return self.getItemsByInterwiki([site], [title])[0]

    def save(self, items, comment=u''):
        if type(items) != list:
            items = [items]
        for item in items:
            params = {"action":"wbsetitem", "clear": ""}
            if item.id:
                params["id"] = item.id
            data = {"sitelinks": item.sitelinks, "aliases": item.aliases, "labels": item.labels, "descriptions": item.descriptions}
            params["data"] = json.dumps(data, ensure_ascii=False)
            newdata = self.request.postWithToken(params)
            self._createItem(newdata["item"], item)

    def _createItemCollection(self, data):
        items = []
        for item in data:
            i = self._createItem(data[item])
            items.append(i)
        return items

    def _createItem(self, item, target=None):
        if not "sitelinks" in item:
            item["sitelinks"] = {}
        if not "aliases" in item:
            item["aliases"] = {}
        if not "labels" in item:
            item["labels"] = {}
        if not "descriptions" in item:
            item["descriptions"] = {}

        sitelinks = {}
        for x in item["sitelinks"]:
            sitelinks[x] = item["sitelinks"][x]["title"]
        aliases = {}
        for x in item["aliases"]:
            aliases[x] = [y["value"] for y in item["aliases"][x]]
        labels = {}
        for x in item["labels"]:
            labels[x] = item["labels"][x]["value"]
        descriptions = {}
        for x in item["descriptions"]:
            descriptions[x] = item["descriptions"][x]["value"]
        if target:
            target.sitelinks = sitelinks
            target.aliases = aliases
            target.labels = labels
            target.descriptions = descriptions
            if target.id and target.id != item["id"]:
                raise errors.ItemIDMismatch("Local item id does not match remote id. Have you added manually the id?")
            else:
                target.id = item["id"]
            return target
        else:
            i = Item(sitelinks, aliases, labels, descriptions)
            i.id = item["id"]
            return i
