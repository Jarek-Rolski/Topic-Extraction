import requests
import datetime
from datetime import datetime

# Preprocess singular request into required format
def processed_data(req):
    req_json = req.json()
    
    data = []
    
    for review in req_json['data']['reviews']:
        # Date of last modification of comment
        date = datetime.strptime(review['Modified'],"%Y-%m-%d %H:%M:%S")
        # Separated positive comment with ratings
        pros = (review['LikesText'], [p['Name'] for p in review['RatingDistribution'] if p['count']>3])
        # Separated negative comment with ratings
        cons = (review['DisLikesText'], [p['Name'] for p in review['RatingDistribution'] if p['count']<3])
        
        data.append([pros, cons, date])
    return data


# Scrap all comments between start_date and end_date(excluding end date) using api
def get_comments(start_date, end_date):
    
    # Find starting page in optimal way
    i = 1
    req = requests.get('https://www.ambitionbox.com/api/v2/reviews/data/114?page=1&sort=recent')
    j = req.json()['data']['pagination']['total_pages']
    while True:
        k = (j-i)//2 + i

        req = requests.get('https://www.ambitionbox.com/api/v2/reviews/data/114?page='+str(k)+'&sort=recent')
        
        if datetime.strptime(req.json()['data']['reviews'][0]['Modified'],"%Y-%m-%d %H:%M:%S") > end_date:
            i = k
        else:
            j = k
    
        if j-i < 2:
            break
            
    # Starting page
    page = i
    data = []
    while True:
        req = requests.get('https://www.ambitionbox.com/api/v2/reviews/data/114?page='+str(page)+'&sort=recent')
    
        # Stop when there is no more pages to scrap
        if req.status_code != 200:
            return data
        
        prep = processed_data(req)
        for review in prep:
            # Stop when we get comments before January 2022
            if review[2] < start_date:
                return data
            # Add comments for January 2022
            if review[2] < end_date and review[2] >= start_date:
                data.append(review)
                
        page += 1
    return data