from pymongo import MongoClient

client = MongoClient('localhost', 27017)


def write_positions_db(positions_data, db_name=None):
    if db_name:
        db = client[db_name]
    else:
        raise Exception('Please, give db name')

    if positions_data:

        matched = 0
        modified = 0
        for position_data in positions_data:

            keys_only = {'ad_id', 'position', 'place'}
            position_data = {k: position_data[k] for k in keys_only}
            print(position_data)
            result = db.positions.update_many(
                {"ad_id": position_data['ad_id']},
                {'$set': position_data},
                upsert=True
            )
            matched += result.matched_count
            modified += result.modified_count
        print('Matched: {}, modified {}'.format(matched, modified))


def main():
    pass


if __name__ == '__main__':
    main()
