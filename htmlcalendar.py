"""
  html-calendar
  =============

  A simple HTML calendar generator with callbacks for adding links to date
  and formating classes
"""

__version__ = "0.0.8"

import calendar
import datetime
from datetime import datetime as dt

def nolist(date):
    return []


def nostr(date):
    return ""


def no_month_factory(no_month_class):
    def no_month(date):
        return [no_month_class]
    return no_month


WEEKDAYS0 = list(calendar.day_abbr)
WEEKDAYS1 = [WEEKDAYS0[6]] + list(WEEKDAYS0[0:6])
EMPTY_ROW = "<tr>" + 7 * '<td class="nomonth">&nbsp;</td>' + "</tr>"


def htmlday(date, classes, classes_today, links, td_custom_attribute_string, is_selected):
    result = []
    cs = classes(date)    
    ls = links(date)

    other_attributes_strings = ""
    if len(td_custom_attribute_string.strip()) > 0:
        other_attributes_strings = " " + td_custom_attribute_string.replace("[[date]]", dt.strftime(date, '%Y-%m-%d') )

    merged_class_values = ""
    common_class_values = ""
    today_class_values = ""
    selected_class_value = ""
    if cs:
        common_class_values = " ".join(cs)        

    if classes_today:
        today_class_values = " ".join(classes_today)

    if is_selected:
        selected_class_value = "selected"

    merged_class_values = common_class_values + " " + today_class_values + " " + selected_class_value 

    if len(merged_class_values.strip()) > 0:
        result.append(f'<td class="{merged_class_values.strip()}"{other_attributes_strings}>')
    else:
        result.append(f"<td{other_attributes_strings}>") #result.append('<td role="button">')


    if ls:
        result.append(f'<a href="{ls}">')
    result.append(str(date.day))
    if ls:
        result.append("</a>")
    result.append("</td>")
    return "".join(result)


def html_week_days(caltype):
    result = ["<tr>"]
    wds = WEEKDAYS1 if caltype else WEEKDAYS0
    for wd in wds:
        result.append(f"<th>{wd}</th>")
    result.append("</tr>\n")
    return "".join(result)


def htmlmonth(month, year, classes=nolist, links=nostr, nomonth=nolist,
              th_classes=[], table_classes=[], table_id="", caltype=0, show_year=True, show_month=True,
              classes_today=[], currentSelectedDate=datetime.date.today(), td_custom_attribute_string=""):
    result = []
    week_count = 0
    if show_year:        
        result.append(f"<h1>{year}</h1>")
    if show_month:
        result.append(f"<h2>{calendar.month_name[month]}</h2>")
    
    table_attributes = ""
    table_id_attribute = ""
    table_class_attribute = ""
    if table_id.strip() != "":
        table_id_attribute = f'id="{table_id}"'
    if table_classes:
        cls = ' '.join(table_classes)     
        table_class_attribute = f'class="{cls}"'                    
    table_attributes = (table_id_attribute + ' ' + table_class_attribute).strip()
    if table_attributes != "":
        result.append(f'<table {table_attributes}>')
    else:
        result.append('<table>')

    result.append(html_week_days(caltype))
    cal = calendar.Calendar(caltype)
    for date in cal.itermonthdates(year, month):
        is_selectedDate = False
        if date == currentSelectedDate:
            is_selectedDate = True

        if date.weekday() == 0:
            week_count += 1
            result.append("<tr>\n")
        if date.month != month:
            result.append(htmlday(date, nomonth, [], nostr, "", False))
        elif date == date.today():
            result.append(htmlday(date, classes, classes_today, links, td_custom_attribute_string, is_selectedDate))
        else:
            result.append(htmlday(date, classes, [], links, td_custom_attribute_string, is_selectedDate))
        if date.weekday() == 6:
            result.append("</tr>\n")
    if week_count == 5:
        result.append(EMPTY_ROW)
    result.append("</table>\n\n")
    return "".join([str(x) for x in result])


def backwards_iterator(starting, months):
    month = starting.month
    year = starting.year
    yield (starting.month, starting.year)
    for i in range(0, months):
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        yield (month, year)


def forward_iterator(starting, months):
    month = starting.month
    year = starting.year
    yield (starting.month, starting.year)
    for i in range(0, months):
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        yield (month, year)


def htmlcalendar(starting_date,
                 months=3,
                 classes=nolist,
                 links=nostr,
                 no_month_class='nomonth',
                 th_classes=[],
                 table_classes=[],
                 table_id="",
                 caltype=0,
                 backwards=True,
                 show_year=True, 
                 show_month=True,
                 classes_today=[],
                 currentSelectedDate=datetime.date.today(),
                 td_custom_attribute_string=""):
    """
    Main function that takes a starting date and returns a list of
    tables containing months calendars in tables.

    All tables generated have 6 rows, even the last one is empty.

    Parameters
    ----------

    starting_date: datetime.date
        Any date object of the month we want to start generating from.
    months: int
        The number of months we want to generate
    classes: function
        A function that takes a datetime.date as parameter and returns
        a list of strings that will be put as classes of the table cell
    links: function
        A function that takes a datetime.date as parameter and returns
        a fully qualified URL that will be linked to the date number. If
        the function returns none there is no link generated.
    no_month_class: string
        The name of a css class to be put in the cells of the table that
        don't belongo to the month in course.
    th_classes: list
        A list of classes to be put in each one of the weekdays labels.
    table_classes: list
        A list of classes to be put in the main table object.
    caltype: int
        If you want weeks starting on sunday 1 else 0
    backwards: bool
        If you want to generate the calendars to the past True else False
    show_year: bool
        If you want to show year label at the top of the calendar
    show_month: bool
        If you want to show month label at the top of the calendar
    """

    nomonth = no_month_factory(no_month_class)

    iterator = backwards_iterator if backwards else forward_iterator

    result = []
    for month, year in iterator(starting_date, months - 1):
        result.append(htmlmonth(month, year, 
                                classes=classes, 
                                links=links, 
                                nomonth=nomonth,
                                th_classes=th_classes, 
                                table_classes=table_classes, 
                                table_id=table_id, 
                                caltype=caltype, 
                                show_year=show_year, 
                                show_month=show_month,
                                classes_today=classes_today,
                                currentSelectedDate=currentSelectedDate,
                                td_custom_attribute_string=td_custom_attribute_string)
        )
    return reversed(result)
