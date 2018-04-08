from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
import operator

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

class TScan(db.Model): # Table for storing training data
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
        return '<TScan %r>' % (self.indexID)

class PScan(db.Model): # Table for storing mean of all the training data
    id=db.Column(db.Integer,primary_key=True)
    indexID = db.Column(db.Integer)
    macID=db.Column(db.String(48))
    rssi_value=db.Column(db.Float)
    count = db.Column(db.Integer)

    def __init__(self,indexID,macID,rssi_value,count):
        self.indexID=indexID
        self.macID=macID
        self.rssi_value=rssi_value
        self.count=count
    def __repr__(self):
        return '<ProcessScan %r>' % (self.indexID)

class PScan1(db.Model): # Table for storing mean of all the training data
    id=db.Column(db.Integer,primary_key=True)
    indexID = db.Column(db.Integer)
    macID=db.Column(db.String(48))
    rssi_value=db.Column(db.Float)

    def __init__(self,indexID,macID,rssi_value):
        self.indexID=indexID
        self.macID=macID
        self.rssi_value=rssi_value
    def __repr__(self):
        return '<ProcessScan %r>' % (self.indexID)

db.create_all()
@app.route('/')
def index():
    return "hello world"

@app.route('/getTrainingScans',methods=['GET','POST'])
def getTrainingScans():
    if request.method=="POST":
        macIDCount= int(request.form['macIDcount'])
        indexID = int(request.form['indexID'])
        scanID = 0
        result = db.session.execute("SELECT scans FROM points WHERE indexID = %s" % indexID).fetchall()

        count = 0

        for row in result:
            count = count + 1
        if count == 0:
            scanID = 1
            location = 'temp'
            result = db.session.execute('insert into points(indexID,location,scans) values (%d,"%s", %d)' % (indexID, location, scanID))
            db.session.commit()
        else:
            for row in result:
                scanID = row['scans']
            scanID = scanID + 1
            result = db.session.execute("UPDATE points set scans = scans + 1 where indexID = %d" % indexID)
            db.session.commit()

        for i in range(0,macIDCount):
            macID=request.form['macID'+ '[' + str(i) + ']']
            ssid=request.form['ssid'+ '[' + str(i) + ']']
            rssi_value=request.form['rssi_value'+ '[' + str(i) + ']']
            scanData=Scan(indexID,macID,ssid,rssi_value,scanID)
            db.session.add(scanData)
            db.session.commit()
        return str(indexID)
    else:
        return jsonify(status_code=500)



@app.route('/getProcessScans',methods=['GET','POST']) #To find location of user
def getProcessScans():
    if request.method=="POST":
        print "Entered in processing"
        macIDCount= int(request.form['macIDcount'])
        macID=[]
        level=[]
        # To store macID - rssi_value pairs
        mac_rssi = {}

        print macIDCount

        # Store macid and rssi_value of each and every AP recerived from the client
        for i in range(0,macIDCount):
            mac_rssi[request.form['macID['+str(i)+']']] = float(request.form['rssi_value['+str(i)+']'])
            macID.append(request.form['macID['+str(i)+']'])
            level.append(float(request.form['rssi_value['+str(i)+']']))
        print mac_rssi

        return testFunction(macID,level,mac_rssi)
    else:
        return jsonify(status_code=500)


@app.route('/getProcessScansNormal',methods=['GET','POST'])
def getProcessScansNormal():
    if request.method=="POST":
        print "Entered in processing"
        macIDCount= int(request.form['macIDcount'])
        macID=[]
        level=[]
        # To store macID - rssi_value pairs
        mac_rssi = {}

        print macIDCount

        # Store macid and rssi_value of each and every AP recerived from the client
        for i in range(0,macIDCount):
            mac_rssi[request.form['macID['+str(i)+']']] = float(request.form['rssi_value['+str(i)+']'])
            macID.append(request.form['macID['+str(i)+']'])
            level.append(float(request.form['rssi_value['+str(i)+']']))
        print mac_rssi

        # Find the index points having atleast one of the APs in the received APs
        query_result  = db.session.execute("SELECT DISTINCT `p_scan`.`indexID` FROM `p_scan` WHERE `p_scan`.`macID` IN ('%s')" % str("','".join(macID)) ).fetchall()
        #print query_result[0]['indexID']

        indexID_set = []

        # Store the set of all the points in a list
        for row in query_result:
            indexID_set.append(row['indexID'])

        #print indexID_set

        least_distance = -1
        user_location = 0

        result_mac = []

        result_index = {}

        rssi_threshold = -80
        for i in range(0,len(indexID_set)):
            query_result  = db.session.execute("SELECT `p_scan1`.`macID`,`p_scan1`.`rssi_value` FROM `p_scan1` WHERE `p_scan1`.`indexID` = ('%s')" % indexID_set[i] ).fetchall()
            distance = 0.0

            for  row in query_result:
                if (row['macID'] in mac_rssi and row['rssi_value']> rssi_threshold) or (row['macID'] in mac_rssi and mac_rssi[row['macID']] > rssi_threshold): # To find if rssi_value crosses threshold
                    result_mac.append(row['macID'])
                    distance = distance + (float(row['rssi_value']) - mac_rssi[row['macID']]) ** 2
                elif row['rssi_value'] > rssi_threshold: # row not present in live tuple
                    distance = distance + (100 + row['rssi_value']) ** 2
                else:
                    pass

            for row in macID:
                if row not in result_mac:
                    if mac_rssi[row] > rssi_threshold:
                        distance = distance + (100 + mac_rssi[row]) ** 2

            result_index[indexID_set[i]] = distance

            # If you find a point with lesser distance
            if least_distance == -1 or distance < least_distance:
                least_distance = distance
                user_location = indexID_set[i]


        sorted_x = sorted(result_index.items(), key=operator.itemgetter(1))


        print sorted_x
        return str(sorted_x[0][0]) + " or " + str(sorted_x[1][0])
    else:
        return jsonify(status_code=500)


@app.route('/getUpdateScans',methods=['GET','POST'])
def getUpdateScans():
    if request.method=="POST":

        alpha = 0.05

        print "Eneterd update"
        macIDCount= int(request.form['macIDcount'])
        indexID = int(request.form['indexID']) # To know correct location corresponding to a mac-rssi tuple
        macID=[]
        level=[]
        # To store macID - rssi_value pairs
        mac_rssi = {}

        print macIDCount

        # Store macid and rssi_value of each and every AP recerived from the client
        for i in range(0,macIDCount):
            mac_rssi[request.form['macID['+str(i)+']']] = float(request.form['rssi_value['+str(i)+']'])
            macID.append(request.form['macID['+str(i)+']'])
            level.append(float(request.form['rssi_value['+str(i)+']']))
        print mac_rssi

        query_result  = db.session.execute("SELECT `p_scan1`.`macID`,`p_scan1`.`rssi_value` FROM `p_scan1` WHERE `p_scan1`.`indexID` = %d" % indexID).fetchall()
        count = 1

        result_mac = []

        for  row in query_result:
            if row['macID'] in mac_rssi: # To find if mac is there in fingerprint
                result_mac.append(row['macID'])
                #Update rssi_value if mac is there
                result = db.session.execute('update p_scan1 set rssi_value = (rssi_value + %f * %f)/(1 + %f) where macID="%s"' % (alpha, mac_rssi[row['macID']], alpha, row['macID']))
                db.session.commit()

        for row in macID: # row in live tuple but not in fingerprint
            if row not in result_mac:
                indexID=indexID
                macID=row
                rssi_value=mac_rssi[row]
                scanData=PScan1(indexID,macID,rssi_value)
                db.session.add(scanData)
                db.session.commit()

        return "Done"
    else:
        return jsonify(status_code=500)

# To compute average and count once training is Done
@app.route('/computeAverage')
def computeAverage():

    db.session.execute("DELETE FROM p_scan")
    db.session.commit()

    db.session.execute("INSERT INTO p_scan(indexID,macID,rssi_value,count) SELECT scan.indexID, scan.macID,avg(rssi_value),count(macID) FROM scan GROUP BY indexID,macID" )
    db.session.commit()

    db.session.execute("DELETE FROM p_scan1")
    db.session.commit()

    db.session.execute("INSERT INTO p_scan1(indexID,macID,rssi_value) SELECT scan.indexID, scan.macID,avg(rssi_value) FROM scan GROUP BY indexID,macID" )
    db.session.commit()
    return "Done"

@app.route('/showScans')
def showScans():
    scans=Scan.query.all()
    for row in scans:
        print row.indexID
    return jsonify(scans=str(scans))


# Get testing data
test_count=266
@app.route('/TgetTrainingScans',methods=['GET','POST'])
def TgetTrainingScans():
    if request.method=="POST":
        global test_count
        test_count = test_count+ 1
        macIDCount= int(request.form['macIDcount'])
        indexID = int(request.form['indexID'])

        for i in range(0,macIDCount):
            macID=request.form['macID'+ '[' + str(i) + ']']
            ssid=request.form['ssid'+ '[' + str(i) + ']']
            rssi_value=request.form['rssi_value'+ '[' + str(i) + ']']
            scanData=TScan(indexID,macID,ssid,rssi_value,test_count)
            db.session.add(scanData)
            db.session.commit()
        return str(indexID)
    else:
        return jsonify(status_code=500)

@app.route('/test')
def test():
    accuracy = 0
    for i in range(1,test_count): # Get each point of test data
        print i
        macID=[]
        level=[]
        # To store macID - rssi_value pairs
        mac_rssi = {}
        indexID = 0
        query_result  = db.session.execute("SELECT indexID,macID,rssi_value FROM t_scan WHERE scanID = %d" % i ).fetchall()
        for row in query_result:
            indexID = row['indexID']
            macID.append(row['macID'])
            level.append(row['rssi_value'])
            mac_rssi[row['macID']] = row['rssi_value']

        if str(indexID) == testFunction(macID,level,mac_rssi):
            accuracy = accuracy + 1
        else:
            accuracy = accuracy
    return "No of correct predictions: " + str(accuracy) + " Total number of test scans: " + str(test_count)


def testFunction(macID,level,mac_rssi): #Test script for finding no of testind data correct

    # Find the index points having atleast one of the APs in the received APs
    query_result  = db.session.execute("SELECT DISTINCT `p_scan`.`indexID` FROM `p_scan` WHERE `p_scan`.`macID` IN ('%s')" % str("','".join(macID)) ).fetchall()
    #print query_result[0]['indexID']

    indexID_set = []

    # Store the set of all the points in a list
    for row in query_result:
        indexID_set.append(row['indexID'])

    #print indexID_set

    least_distance = -1
    user_location = 0

    result_mac = []
    result_index = {}

    rssi_threshold = -87
    for i in range(0,len(indexID_set)):
        query_result  = db.session.execute("SELECT `p_scan`.`macID`,`p_scan`.`rssi_value`,`p_scan`.`count` FROM `p_scan` WHERE `p_scan`.`indexID` = ('%s')" % indexID_set[i] ).fetchall()
        count_result  = db.session.execute("SELECT `points`.`scans` FROM `points` WHERE `points`.`indexID` = ('%s')" % indexID_set[i] ).fetchall()
        distance = 0.0
        count = 1
        for row in count_result:
            count = row['scans']
        #print count
        for  row in query_result:
            if (row['macID'] in mac_rssi and row['rssi_value']> rssi_threshold) or (row['macID'] in mac_rssi and mac_rssi[row['macID']] > rssi_threshold): # To find if rssi_value crosses threshold
                result_mac.append(row['macID'])
                distance = distance + row['count']*(float(row['rssi_value']) - mac_rssi[row['macID']]) ** 2 / count
            elif row['rssi_value'] > rssi_threshold: # row not present in live tuple
                distance = distance + row['count'] * (100 + row['rssi_value']) ** 2 / count
            else:
                pass

        for row in macID:
            if row not in result_mac:
                if mac_rssi[row] > rssi_threshold:
                    distance = distance + (100 + mac_rssi[row]) ** 2

        # for i in range(0,len(indexID_set)):
        #     query_result  = db.session.execute("SELECT `p_scan1`.`macID`,`p_scan1`.`rssi_value` FROM `p_scan1` WHERE `p_scan1`.`indexID` = ('%s')" % indexID_set[i] ).fetchall()
        #     distance = 0.0
        #
        #     for  row in query_result:
        #         if (row['macID'] in mac_rssi and row['rssi_value']> rssi_threshold) or (row['macID'] in mac_rssi and mac_rssi[row['macID']] > rssi_threshold): # To find if rssi_value crosses threshold
        #             result_mac.append(row['macID'])
        #             distance = distance + (float(row['rssi_value']) - mac_rssi[row['macID']]) ** 2
        #         elif row['rssi_value'] > rssi_threshold: # row not present in live tuple
        #             distance = distance + (100 + row['rssi_value']) ** 2
        #         else:
        #             pass
        #
        #     for row in macID:
        #         if row not in result_mac:
        #             if mac_rssi[row] > rssi_threshold:
        #                 distance = distance + (100 + mac_rssi[row]) ** 2

        result_index[indexID_set[i]] = distance

        # If you find a point with lesser distance
        if least_distance == -1 or distance < least_distance:
            least_distance = distance
            user_location = indexID_set[i]


    sorted_x = sorted(result_index.items(), key=operator.itemgetter(1))

    return str(sorted_x[0][0])


if __name__=='__main__':
    app.run(host= '0.0.0.0',debug=True)
