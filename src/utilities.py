import json

punctuation = [",",".",";"]
key_tags = {
    "MD": { #Modal e.g "should", "could"
        "start": 0, 
        "end": 5,
        "before": "",
        "after": [""]
    },
    ":": { #Colon, want to catch anything after - could be an explanation
        "start": 0, 
        "end": float('inf'),
        "before": [":"],
        "after": [":"]
    },
    "VB" : { #Verb at the start of sentence could indicate action
        "start": 0, 
        "end": 1, 
        "before": "",
        "after": [punctuation[1], "MD"]
    }
}

class ConditionalNode: 

    def __init__(self, num=None, data=None, next_node = None, conditional_node=None):
        self.id = num
        self.data = data
        self.conditional_next = conditional_node
        self.next = next_node

    def get_data(self):
        return self.data
    
    def get_conditional(self):
        return self.conditional_next
    
    def get_next(self):
        return self.next
    
    def set_next(self, next_node):
        self.next = next_node
    
    def set_conditional_next(self, conditional):
        self.conditional_next = conditional

class Node:

    def __init__(self, num = None, data = None, next_node = None):
        self.id = num
        self.data = data
        self.next = next_node
        self.activation_words = [
            "go next", "next", "continue", "skip"
        ]
    
    def get_id(self):
        return self.id

    def get_data(self):
        return self.data
    
    def get_next(self):
        return self.next
    
    def set_next(self, next_node):
        self.next = next_node
    
class LinkedList: 
    
    def __init__(self, head=None):
        self.head = head
        self.tail = None
        self.count = 0

    def insert(self, data):
        #We want to insert at back of linked list
        self.count += 1
        new_node = Node(num=self.count, data=data)
        if not self.head: 
            self.head = new_node
        elif not self.tail:
            self.head.set_next(new_node)
            if isinstance(self.head, ConditionalNode):
                self.head.get_conditional().set_next(new_node)
            self.tail = new_node 
        else: 
            self.tail.set_next(new_node)
            if isinstance(self.tail, ConditionalNode):
                self.tail.get_conditional().set_next(new_node)
            self.tail = new_node
    
    def insert_conditional(self, data, conditional):
        self.count += 1
        new_node = ConditionalNode(num=self.count, data=data)
        conditional = Node(num=self.count, data=conditional)
        new_node.set_conditional_next(conditional)
        if not self.head:
            self.head = new_node
        elif not self.tail:
            self.head.set_next(new_node)
            if isinstance(self.head, ConditionalNode):
                self.head.get_conditional().set_next(new_node)
            self.tail = new_node
        else: 
            self.tail.set_next(new_node)
            if isinstance(self.tail, ConditionalNode):
                self.tail.get_conditional().set_next(new_node)
            self.tail = new_node
    
    def find(self, number, data = None):
        curr = self.head 
        while curr:
            if curr.get_id() == number \
                or data \
                    and curr.get_data() == data:
                return curr
        return None
    
    def delete(self, data):
        #Only iterate from start shouldn't be too long
        curr = self.head
        prev = None
        while curr: 
            if curr.get_data() == data:
                #At head - set new head
                if not prev: 
                    self.head = curr.get_next()
                #At tail - set new tail 
                if not curr.get_next(): 
                    prev.set_next(None)
                    self.tail = prev
                else: 
                    prev.set_next(curr.get_next())
            else: 
                prev = curr
                curr = curr.get_next()

    def printList(self):
        temp = self.head
        while temp: 
            print(temp.get_data())
            temp = temp.get_next()
    
    def getList(self):
        temp = self.head 
        llist = []
        while temp:
            llist.append(temp.get_data())
            if isinstance(temp, ConditionalNode):
                llist.append(temp.get_conditional().get_data())
            temp = temp.get_next()
        return llist
    
    def to_json(self) -> str:
        return json.dumps(self.getList())
    
    def from_json(self, json: str):
        ll_list = json.loads(json)
        for node in ll_list:
            self.insert(node)
