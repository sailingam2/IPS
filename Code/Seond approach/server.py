from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/sample'
db = SQLAlchemy(app)

class Scan(db.Model): # Table for storing training data
    id=db.Column(db.Integer,primary_key=True)
    indexID=db.Column(db.Integer)
    macID=db.Column(db.String(48))
    ssid=db.Column(db.String(48))
    rssi_value=db.Column(db.Integer)
    scanID=db.Column(db.String(32))

    def __init__(self, indexID,macID,ssid,rssi_value,scanID):
        self.indexID=indexID
        self.macID=macID
        self.ssid=ssid
        self.rssi_value=rssi_value
        self.scanID=scanID

    def __repr__(self):
        return '<Scan %r>' % (self.indexID)

class PScan(db.Model): # Table for storing mean of all the training data
    id=db.Column(db.Integer,primary_key=True)
    indexID = db.Column(db.Integer)
    macID=db.Column(db.String(48))
    rssi_value=db.Column(db.Integer)
    count = db.Column(db.Integer)

    def __init__(self,indexID,macID,rssi_value,count):
        self.indexID=indexID
        self.macID=macID
        self.rssi_value=rssi_value
        self.count=count
    def __repr__(self):
        return '<ProcessScan %r>' % (self.indexID)
db.create_all()
@app.route('/')
def index():
    return "hello world"

@app.route('/getTrainingScans',methods=['GET','POST'])
def getTrainingScans():
    if request.method=="POST":
        indexID=request.form['indexID']
        macID=request.form['macID']
        ssid=request.form['ssid']
        rssi_value=request.form['rssi_value']
        scanID=request.form['scanID']
        scanData=Scan(indexID,macID,ssid,rssi_value,scanID)
        db.session.add(scanData)
        db.session.commit()
        return jsonify(done=200,message='Successfully recorded')
    else:
        return jsonify(status_code=500)

@app.route('/getProcessScans',methods=['GET','POST'])
def getProcessScans():
    if request.method=="GET":
        macIDCount=request.args.get('macIDCount')
        macIDCount=int(macIDCount)
        macID=[]
        level=[]
        # To store macID - rssi_value pairs
        mac_rssi = {}

        print macIDCount

        # Store macid and rssi_value of each and every AP recerived from the client
        for i in range(0,macIDCount):
            mac_rssi[request.args.get('macID['+str(i)+']')] = int(request.args.get('rssi_value['+str(i)+']'))
            macID.append(request.args.get('macID['+str(i)+']'))
            level.append(request.args.get('rssi_value['+str(i)+']'))
        print mac_rssi

        # Find the index points having atleast one of the APs in the received APs
        query_result  = db.session.execute("SELECT DISTINCT `p_scan`.`indexID` FROM `p_scan` WHERE `p_scan`.`macID` IN ('%s')" % str("','".join(macID)) ).fetchall()
        print query_result[0]['indexID']

        indexID_set = []

        # Store the set of all the points in a list
        for row in query_result:
            indexID_set.append(row['indexID'])

        print indexID_set

        least_distance = -1
        user_location = 0
        # For each indexID, compare it with received tuple and find distance
        for i in range(0,len(indexID_set)):
            query_result  = db.session.execute("SELECT `p_scan`.`macID`,`p_scan`.`rssi_value` FROM `p_scan` WHERE `p_scan`.`indexID` = ('%s')" % indexID_set[i] ).fetchall()
            distance = 0
            for  row in query_result:
                if row['macID'] in mac_rssi:
                    distance = distance + (row['rssi_value'] - mac_rssi[row['macID']]) ** 2
                else:
                    distance = distance + (row['rssi_value']) ** 2

            # If you find a point with lesser distance
            if least_distance == -1 or distance < least_distance:
                least_distance = distance
                user_location = indexID_set[i]

        #for i in range(0,)
        # indexID_set=PScan.query.with_entities(PScan.indexID).filter(PScan.macID.in_(macID)).distinct()
        # print indexID_set

        print user_location
        return jsonify(status_code=200,message="Successfully processed",macID=macID,rssi_value=level)
    else:
        return jsonify(status_code=500)

# To compute average and count once training is Done
@app.route('/computeAverage')
def computeAverage():

    db.session.execute("INSERT INTO p_scan(indexID,macID,rssi_value,count) SELECT scan.indexID, scan.macID,avg(rssi_value),count(macID) FROM scan GROUP BY indexID,macID" )
    db.session.commit()
    return "Done"

@app.route('/showScans')
def showScans():
    scans=Scan.query.all()
    for row in scans:
        print row.indexID
    return jsonify(scans=str(scans))

if __name__=='__main__':
    app.run(host= '0.0.0.0',debug=True)
