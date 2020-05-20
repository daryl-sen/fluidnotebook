from project.models import Pages
from project import db
import time

def page_add(rec_heading, rec_content, rec_notebook_id, rec_author):
    # 1. Find last item
    last_item = Pages.query.filter_by(notebook = rec_notebook_id).filter_by(next=0).first()

    # 2. Create new item, new item prior = last item ID, new item next = 0
    new_item = Pages(prior = last_item.id, next = 0, heading = rec_heading, content = rec_content, last_update = int(time.time()), notebook = rec_notebook_id, author = rec_author)
    db.session.add(new_item)
    db.session.commit()

    # 3. Set last item next to new item ID
    last_item.next = new_item.id
    db.session.commit()

    return new_item.id




# insertion_point is the item prior to where the item will be inserted
def page_insert(position, insertion_point, rec_heading, rec_content, rec_notebook_id, rec_author):

    if position == "after":
        # 1. set new item prior = IP ID, new item next = IP next
        ip_row = Pages.query.get(insertion_point)
        new_item = Pages(prior = ip_row.id, next = ip_row.next, heading = rec_heading, content = rec_content, last_update = int(time.time()), notebook = rec_notebook_id, author = rec_author)
        db.session.add(new_item)
        db.session.commit()

        # 2. IP next.prior = new item ID
        after_ip = Pages.query.get(ip_row.next)
        after_ip.prior = new_item.id

        # 3. IP next = new item ID
        ip_row.next = new_item.id
        db.session.commit()

        return new_item.id

    elif position == "before":
        ip_row = Pages.query.get(insertion_point)
        new_item = Pages(prior = ip_row.prior, next = ip_row.id, heading = rec_heading, content = rec_content, last_update = int(time.time()), notebook = rec_notebook_id, author = rec_author)
        db.session.add(new_item)
        db.session.commit()


        prior_row = Pages.query.get(ip_row.prior)
        prior_row.next = new_item.id

        ip_row.prior = new_item.id
        db.session.commit()

        return new_item.id




# item id
def page_delete(target_id):
    target_item = Pages.query.get(target_id)

    prior_ref = Pages.query.filter_by(prior=target_item.id).first()
    if prior_ref is not None:
        prior_ref.prior = target_item.prior

    next_ref = Pages.query.filter_by(next=target_item.id).first()
    next_ref.next = target_item.next

    db.session.delete(target_item)

    db.session.commit()

def page_swap(item_x, item_y):
    item_x = Pages.query.get(item_x)
    item_y = Pages.query.get(item_y)

    item_x_title = item_x.title
    item_x.title = item_y.title
    item_y.title = item_x_title
    db.session.commit()



def create_sorted_list(rec_notebook_id):

    #retrieve unorder list
    all_pages = Pages.query.filter_by(notebook = rec_notebook_id)

    #declare a dictionary
    page_dict = {}

    #add pages to dictionary
    for page in all_pages:
        page_dict.update({page.id:{'id':page.id, 'heading':page.heading, 'next':page.next}})

    #find first page
    first_page = Pages.query.filter_by(notebook = 1).filter_by(prior = 0).first()

    #define list
    sorted_seq = []

    #add first item to list
    sorted_seq.append({'id':first_page.id, 'heading':first_page.heading, 'next':first_page.next})

    #add items based on the next value, for sorting
    i = 0
    for i in range(0, all_pages.count()-1):
        sorted_seq.append(page_dict[sorted_seq[i]['next']])

    sorted_seq.pop(0)
    print(sorted_seq)
    return sorted_seq



##### Old method, involves delete then reinsert, doesn't work 2 ways
# # model is the name of the table where the operations will take place, item_x is the first item, item_y is the second item. Order is arbitrary
# def swap(item_x, item_y):
#     item_y = Pages.query.get(item_y)
#
#     # store item y values before deleting
#     item_y_title = item_y.title
#     item_y_next = item_y.next
#
#     delete(item_y.id)
#
#     item_x = Pages.query.get(item_x)
#     ip_row = Pages.query.get(item_x.prior)
#
#     # print("\n\n\n ID: {}, title: {} \n\n\n".format(ip_row.id, ip_row.title))
#
#     new_item_y = Pages(prior = ip_row.id, next = ip_row.next, title = item_y_title)
#     db.session.add(new_item_y)
#     db.session.commit()
#
#     ip_next = Pages.query.get(ip_row.next)
#
#     ip_next.prior = new_item_y.id
#     ip_row.next = new_item_y.id
#
#     db.session.commit()
