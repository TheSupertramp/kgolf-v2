import os
import datetime
from sqlalchemy import BindParameter, cast, create_engine, text, insert, MetaData, Table, Column
import uuid
import binascii
from Crypto.Cipher import AES
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
 

# DB stuff

db_connection_string = os.environ['DB_CONNECTION_STRING']

engine = create_engine(
    db_connection_string,
    connect_args={
        "ssl": {
            "ssl_ca": "/etc/ssl/cert.pem"
        }
    })

def get_bays():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM Bay WHERE IsActive = 1"))        
        bays = [b._asdict() for b in result.all()]  
        return bays
    
def get_bookingType():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM BookingType WHERE IsActive = 1"))        
        bookingTypes = [b._asdict() for b in result.all()]  
        return bookingTypes   
    
def get_timeslots():
    query = "SELECT "\
	        "   *,"\
            "   time_format(TS.TimeValue, '%l %p') AS `HourNameDisplay`,"\
            "   time_format(TS.TimeValue, '%l:%i %p') AS `HourMinuteNameDisplay`"\
            "FROM kgolf.Timeslot TS"
    with engine.connect() as conn:
        result = conn.execute(text(query))
        timeslots = [ts._asdict() for ts in result.all()]
        return timeslots
    
def get_bookings(bookingDate, bayID):
    query =  "SELECT"\
            " 	TS.*,"\
            "     time_format(TS.TimeValue, '%l:%i %p') AS `HourNameDisplay`,"\
            "     CASE"\
            " 		WHEN lag(Bookings.BookingID) OVER (partition by Bookings.BookingID order by TS.ID ASC) IS NULL AND Bookings.BookingID IS NOT NULL THEN"\
            " 			'Start'"\
            " 		WHEN lead(Bookings.BookingID) OVER (partition by Bookings.BookingID order by TS.ID ASC) IS NULL AND Bookings.BookingID IS NOT NULL THEN"\
            " 			'End'"\
            " 		WHEN lag(Bookings.BookingID) OVER (partition by Bookings.BookingID order by TS.ID ASC) = lead(Bookings.BookingID) OVER (partition by Bookings.BookingID order by TS.ID ASC) THEN"\
            " 			'Between'"\
            " 		ELSE"\
            " 			NULL"\
            " 	  END AS `BookingTimePoint`,"\
            "     Bookings.*"\
            " FROM Timeslot TS"\
            " LEFT JOIN LATERAL ("\
            " 	SELECT"\
            " 		BH.ID As `BookingID`,"\
            "         BH.BookingDate,"\
            "         BH.BayID,"\
            "         BH.BookingTypeID,"\
            "         BH.CustomerID,"\
            "         IFNULL(BH.BookingDescription,'') AS `BookingDescription`,"\
            "         BH.IP,"\
            "         BH.IsActive AS `IsBookingActive`,"\
            "         BH.IsCancelled AS `IsBookingCancelled`,"\
            "         BH.IsPaid,"\
            "         BTD.IsBufferTime,"\
            "         BT.Name AS `BookingTypeName`,"\
            "         BT.Description AS `BookingTypeDescription`"\
            "     FROM BookingHeader BH"\
            "     INNER JOIN BookingTimeDetail BTD"\
            " 		ON BH.ID = BTD.BookingHeaderID"\
            " 	INNER JOIN BookingType BT"\
            " 		ON BH.BookingTypeID = BT.ID"\
            " 	INNER JOIN Bay Bay"\
            " 		ON Bay.ID = BH.BayID"\
            " 	WHERE"\
            " 		TS.ID = BTD.TimeslotID"\
            "         AND BH.IsActive = 1"\
            " 		AND BH.BookingDate = '" + bookingDate.strftime('%Y-%m-%d') +"'"\
            " 		AND BH.BayID = " + str(bayID) + \
            "         AND BTD.IsActive = 1"\
            " ) Bookings ON 1=1"\
            " ORDER BY"\
            " 	TS.ID ASC,"\
            "   CASE WHEN BookingTimePoint = 'End' THEN 0 ELSE 1 END ASC"
    with engine.connect() as conn:
        result = conn.execute(text(query))
        bookings = [bk._asdict() for bk in result.all()]
        return bookings        


def get_availableStartTimeslots(strBookingDate, bayID):
    query = f"""
            SELECT
                TS.*,
                time_format(TS.TimeValue, '%l:%i %p') AS `HourNameDisplay`    
            FROM Timeslot TS
            LEFT JOIN  (
                SELECT
                    BH.ID As `BookingID`,        
                    BTD.TimeslotID,
                    CASE
                        WHEN lag(BH.ID) OVER (partition by BH.ID order by BTD.TimeslotID ASC) IS NULL AND BH.ID IS NOT NULL THEN
                            'Start'
                        WHEN lead(BH.ID) OVER (partition by BH.ID order by BTD.TimeslotID ASC) IS NULL AND BH.ID IS NOT NULL THEN
                            'End'
                        WHEN lag(BH.ID) OVER (partition by BH.ID order by BTD.TimeslotID ASC) = lead(BH.ID) OVER (partition by BH.ID order by BTD.TimeslotID ASC) THEN
                            'Between'
                        ELSE
                            NULL
                    END AS `BookingTimePoint`
                FROM BookingHeader BH		
                INNER JOIN BookingTimeDetail BTD 
                    ON BH.ID = BTD.BookingHeaderID	        	
                WHERE
                    BH.IsActive = 1        
                    AND BH.BookingDate = '{strBookingDate}'
                    AND BH.BayID = {bayID}           
                    AND BTD.IsActive = 1
            ) Bookings 
                ON TS.ID = Bookings.TimeslotID
                    AND Bookings.BookingTimePoint != 'End'
            WHERE
                Bookings.BookingID IS NULL 
            ORDER BY
                TS.ID ASC                
            """    
    with engine.connect() as conn:
        result = conn.execute(text(query))
        availableTimeslots = [ts._asdict() for ts in result.all()]
        return availableTimeslots          


def get_availableEndTimeslots(strBookingDate, bayID):
    query = f"""
            SELECT
                TS.*,
                time_format(TS.TimeValue, '%l:%i %p') AS `HourNameDisplay`    
            FROM Timeslot TS
            LEFT JOIN  (
                SELECT
                    BH.ID As `BookingID`,        
                    BTD.TimeslotID,
                    CASE
                        WHEN lag(BH.ID) OVER (partition by BH.ID order by BTD.TimeslotID ASC) IS NULL AND BH.ID IS NOT NULL THEN
                            'Start'
                        WHEN lead(BH.ID) OVER (partition by BH.ID order by BTD.TimeslotID ASC) IS NULL AND BH.ID IS NOT NULL THEN
                            'End'
                        WHEN lag(BH.ID) OVER (partition by BH.ID order by BTD.TimeslotID ASC) = lead(BH.ID) OVER (partition by BH.ID order by BTD.TimeslotID ASC) THEN
                            'Between'
                        ELSE
                            NULL
                    END AS `BookingTimePoint`
                FROM BookingHeader BH		
                INNER JOIN BookingTimeDetail BTD 
                    ON BH.ID = BTD.BookingHeaderID	        	
                WHERE
                    BH.IsActive = 1        
                    AND BH.BookingDate = '{strBookingDate}'
                    AND BH.BayID = {bayID}           
                    AND BTD.IsActive = 1
            ) Bookings 
                ON TS.ID = Bookings.TimeslotID
                    AND Bookings.BookingTimePoint != 'Start'
            WHERE
                Bookings.BookingID IS NULL 
            ORDER BY
                TS.ID ASC                
            """    
    with engine.connect() as conn:
        result = conn.execute(text(query))
        availableTimeslots = [ts._asdict() for ts in result.all()]
        return availableTimeslots              
    
def insert_Booking(bookingDate, bayID, bookingTypeID, startTimeslotID, endTimeslotID, custFirstname, custLastname, custEmail, custPhone, bookingPassword):
    #Validate the booking details once again    
    result_dict = {}    
    #1. ensure bookingDate is today or future
    if bookingDate < datetime.date.today():        
        result_dict = { 'result': False, 'message': 'Booking date must be today or later.'}
        return result_dict
    #2. booking bayID is valid    
    if isValidBay(bayID) == False:
        result_dict = {'result': False, 'message': 'Invalid bay is selected.'}
        return result_dict
    #3. booking type is valid
    if isValidBookingType(bookingTypeID) == False:
        result_dict = {'result': False, 'message': 'Invalid booking type is selected.'}
        return result_dict        
    #3. booking slotsIDs are valid
    if isValidTimeslot(startTimeslotID) == False or isValidTimeslot(endTimeslotID) == False:
        result_dict = {'result': False, 'message': 'Invalid timeslot is selected.'}
        return result_dict
    if endTimeslotID - startTimeslotID < 2:
        result_dict = {'result': False, 'message': 'booking session must be at least 30 minutes.'}
        return result_dict        
    #4. Check if booking date/bay/slots are available for a new booking.
    if isBookingAvailable(bookingDate, bayID, startTimeslotID, endTimeslotID) == False:
        result_dict = {'result': False, 'message': 'Selected Bay, Date and time is no longer available.'}
        return result_dict
    #5. Ensure Customer info is sufficient
    if custEmail is None or str(custEmail).strip() == '':
        result_dict = {'result': False, 'message': 'Email must be provided for booking.'}
        return result_dict
    if custPhone is None or str(custPhone).strip() == '' or len(str(custPhone).strip()) < 9:
        result_dict = {'result': False, 'message': 'A valid phone number must be provided for booking.'}
        return result_dict
    if bookingPassword is None or bookingPassword.strip() == '':
        result_dict = {'result': False, 'message': 'Booking password is required for you to manage your booking. Otherwise you will not be able to modify or cancel your booking.'}
        return result_dict
    
    # All validation steps has been passed . so let's insert a new booking
    failed_result_dict = {'result': False, 'message': 'Sorry, there was an error processing your booking request. Please try later again or contact by phone if the issue persists.'}
    #1. Add customer
    customerID = AddCustomer(str(custFirstname).strip(), str(custLastname).strip(), str(custEmail).strip(), str(custPhone).strip(), str(bookingPassword))
    if customerID is None or customerID < 0:        
        return failed_result_dict            
    #2. Add Booking Header
    bookingID = AddBookingHeader(bookingDate, bayID, bookingTypeID, customerID)
    if bookingID is None or bookingID < 0:        
        return failed_result_dict    
    #3. Add BookingTime Detail
    isDetailsAdded = AddBookingTimeDetails(bookingID, startTimeslotID, endTimeslotID)
    if isDetailsAdded==True:
        return {'result': True, 'message': 'successfully booked'}
    else:
        return failed_result_dict
    

def isValidBay(bayID):
    return True

def isValidBookingType(bookingTypeID):
    return True

def isValidTimeslot(timeslotID):
    return True

def isBookingAvailable(bookingDate, bayID, startTimeslotID, endTimeslotID):
    return True


def AddCustomer(custFirstname, custLastname, custEmail, custPhone, custPassword):        
    query = text("\
            INSERT INTO \
                Customer \
                (FirstName, LastName, FullName, Mobile, MobileNumericOnly, Email, PW, IsActive, Created, LastUpdated) \
            VALUES \
                (:FirstName, :LastName, :FullName, :Mobile, :MobileNumericOnly, :Email, AES_ENCRYPT(:PW, :MyEncryptKey), :IsActive, :Created, :LastUpdated)")                
            
    with engine.connect() as conn:
        result = conn.execute(query,
                              parameters=dict(FirstName=custFirstname,
                                            LastName=custLastname,
                                            FullName=(custFirstname + ' ' + custLastname),
                                            Mobile=custPhone,
                                            MobileNumericOnly=str(custPhone).lstrip('0'),
                                            Email=custEmail,
                                            PW=custPassword,
                                            MyEncryptKey=custPhone,
                                            IsActive=1,
                                            Created=datetime.datetime.now(),
                                            LastUpdated=datetime.datetime.now()))
        
        if result.lastrowid is not None and result.lastrowid > 0:
            conn.commit()  
            return result.lastrowid                  
        else:
            conn.rollback()
            return None
        


def AddBookingHeader(bookingDate, bayID, bookingTypeID, customerID):
    with engine.connect() as conn:                
        conn_metaData = MetaData()
        bookingHeaderTable = Table("BookingHeader", conn_metaData, autoload_with=conn)
        insertStmt = insert(bookingHeaderTable).values(BookingDate=bookingDate,
                                            BayID=bayID,
                                            BookingTypeID=bookingTypeID,
                                            CustomerID=customerID,                                            
                                            IsActive=1,
                                            IsCancelled=0,
                                            IsPaid=0,
                                            Created=datetime.datetime.now(),
                                            LastUpdated=datetime.datetime.now())        
        result = conn.execute(insertStmt)
        if result.lastrowid is not None and result.lastrowid > 0:
            conn.commit()  
            return result.lastrowid                  
        else:
            conn.rollback()
            return None    
        
def AddBookingTimeDetails(bookingHeaderID, startTimeslotID, endTimeslotID):
    with engine.connect() as conn:
        conn_metaData = MetaData()
        timeDetailTable = Table("BookingTimeDetail", conn_metaData, autoload_with=conn)  
        insertStmt = insert(timeDetailTable).values(
            [{'BookingHeaderID': bookingHeaderID,'TimeslotID': tid,'IsActive': 1, 'IsBufferTime': 0} for tid in range(startTimeslotID, endTimeslotID + 1)]
        )
        result = conn.execute(insertStmt)
        if result.lastrowid is not None and result.lastrowid > 0:
            conn.commit()
            return True
        else:
            conn.rollback()
            return None



# AES Encryption Decryption
key = uuid.uuid4().bytes
"""The encryption key.   Random for this example."""


nonce = uuid.uuid4().bytes
"""for WHERE criteria to work, we need the encrypted value to be the same
each time, so use a fixed nonce if we need that feature.
"""

def aes_encrypt(data):
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    data = data + (" " * (16 - (len(data) % 16)))
    return cipher.encrypt(data.encode("utf-8")).hex()


def aes_decrypt(data):
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt(binascii.unhexlify(data)).decode("utf-8").rstrip()


class EncryptedValue(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        return aes_encrypt(value)

    def process_result_value(self, value, dialect):
        return aes_decrypt(value)        