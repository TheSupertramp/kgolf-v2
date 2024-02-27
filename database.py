from sqlalchemy import create_engine, text
import os
import datetime

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
    
def get_timeslots():
    query = "SELECT "\
	        "   *,"\
            "   time_format(TS.TimeValue, '%l %p') AS `HourNameDisplay`"\
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


