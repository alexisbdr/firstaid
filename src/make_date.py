 
burns = {}
burns["categories"] = ['thermal', 'electrical', 'chemical']
burns['type'] =  {
    'first degree':'Skin is red, dry and painful',
    'second degree':'Skin is red, painful - blisters will appear and skin may appear wet', 
    'third degree':'Skin will be brown or black, sometimes appearing white - may destroy all layers of skin'
    }
burns['steps'] = {
    'thermal': {
        "count": 2,
        "first degree": {
            1:"Cool the burn with large amounts of cold running water",
            2:"Cover the burn with a sterile dressing",
            3:"Minimize shock or thermal exposure",
            4:"Comfort and reassure the person",
        },
        "Third Degree": {
            1:"Get to safety",
            2:"Call and wait for emergency services"
        }
    },
    'chemical': {
        1:"Remove contaminated clothing",
        2:"Flush burn with cold water",
        3:"Call emergency services and keep flushing burn with cold water"
    },
    'electrical': {
        1:"Do not go near the person if they are still in contact with the power source",
        2:"Turn off the power from the source",
        3:"Call 911 - electrical burns require advanced medical care",
        4:"Perform CPR and respiratory emergencies if cardiac arrest",
        5:"Care for shock and thermal burns"
    }
    'general': {

    }
}
