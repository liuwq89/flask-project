import uuid
import traceback
from typing import Optional, Tuple

from flask import abort
from flask import jsonify
from flask import Response
from flask_restful import Resource
from flask_restful import reqparse
from sqlalchemy import desc
from sqlalchemy.orm.query import Query

from app import db, session
from app.common.log import ilog
from app.common.args_conf import ArgsConfig
from app.common.common_func import http_resp
from app.common.common_func import query_data_process
from app.common.interface_control import method_control


class CommonResource(Resource):
    ALLOW_METHOD = dict()

    def __init__(
            self,
            get_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
            put_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
            post_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
            delete_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
        ):
        self.request_id = str(uuid.uuid4())
        self.get_parser_config = get_parser_config or []
        self.put_parser_config = put_parser_config or []
        self.post_parser_config = post_parser_config or []
        self.delete_parser_config = delete_parser_config or []

    @method_control
    def get(self, *args, **kwargs):
        """get method."""
        abort(405)
        pass

    @method_control
    def put(self, *args, **kwargs):
        """put method."""
        abort(405)
        pass

    @method_control
    def post(self, *args, **kwargs):
        """post method."""
        abort(405)
        pass

    @method_control
    def delete(self, *args, **kwargs):
        """delete method."""
        abort(405)
        pass

    @staticmethod
    def get_parser_args(configs: Tuple[ArgsConfig, ...]):
        """get parser args by flask_restful parser."""
        parser = reqparse.RequestParser()
        for config in configs:
            parser.add_argument(**config.to_dict())
        args = parser.parse_args()
        return {k: v for k, v in args.items() if v is not None}

    def http_resp(self, code=1, message="请求成功", data=None, *, status=200):
        """
        return http response.
        
        Egg. code>1 -> success, code=0 -> failed.
        """
        return http_resp(
            code=code,
            message=message,
            data=data,
            request_id=self.request_id,
            status=status,
        )


_GET_COMMON_PARAMS = [
                        ArgsConfig(name="start", type=int, location="args"),
                        ArgsConfig(name="number", type=int, location="args"),
                        ArgsConfig(name="page", type=int, location="args"),
                        ArgsConfig(name="per_page", type=int, location="args"),
                    ]


class _CommonModelResource(CommonResource):
    ALLOW_METHOD = dict()

    def __init__(
            self,
            model=None,
            get_fields: Optional[Tuple[str, ...]] = None,
            date_format: int = 1, # 1: %Y-%m-%d %H:%M:%S, 0: %Y-%m-%d
            json_load_features: Optional[Tuple[str, ...]] = None,
            json_dump_features: Optional[Tuple[str, ...]] = None,
            get_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
            put_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
            post_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
            delete_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
            put_check_exist_fields: Optional[Tuple[str, ...]] = None,
            post_check_exist_fields: Optional[Tuple[str, ...]] = None,
        ):
        CommonResource.__init__(
            self,
            get_parser_config=get_parser_config,
            put_parser_config=put_parser_config,
            post_parser_config=post_parser_config,
            delete_parser_config=delete_parser_config
        )
        self.model = model
        self.date_format = date_format
        self.get_fields = get_fields or []
        self.json_load_features = json_load_features or []
        self.json_dump_features = json_dump_features or []
        self.put_check_exist_fields = put_check_exist_fields or []
        self.post_check_exist_fields = post_check_exist_fields or []

    @staticmethod
    def get_item_by_pid(model, pid):
        """get parser args """
        item = model.query.get(pid) if pid else None
        if getattr(item, "is_delete", 0):
            item = None
        return item
    
    @staticmethod
    def _query_filter_other_logic(model, query: Query, field: str, logic_value: dict):
        """
        process other filter custom-logic.

        Egg. logic_value={"gt": "value"}
        """
        if "gt" in logic_value:
            query = query.filter(getattr(model, field) > logic_value['gt'])
        elif "lt" in logic_value:
            query = query.filter(getattr(model, field) < logic_value['lt'])
        elif 'ge' in logic_value:
            query = query.filter(getattr(model, field) >= logic_value['ge'])
        elif 'le' in logic_value:
            query = query.filter(getattr(model, field) <= logic_value['le'])
        elif 'ne' in logic_value:
            query = query.filter(getattr(model, field) != logic_value['ne'])
        return query
    
    @staticmethod
    def get_item_by_filters(model, fields=None, **filters):
        """get item by filters."""
        equal_filters = {}
        query = model.query
        if hasattr(model, "is_delete"):
            filters["is_delete"] = 0
        for field, value in filters.items():
            if isinstance(value, dict):
                query = _CommonModelResource._query_filter_other_logic(model, query, field, value)
            else:
                equal_filters.update({field: value})
        if equal_filters:
            query = query.filter_by(**equal_filters)
        if fields:
            query = query.with_entities(*[getattr(model, field) for field in fields])
        return query.first()

    @staticmethod
    def get_items_by_filters(model, fields=None, **filters):
        """get items by filters."""
        equal_filters = {}
        query = model.query
        if hasattr(model, "is_delete"):
            filters["is_delete"] = 0
        for field, value in filters.items():
            if isinstance(value, dict):
                query = _CommonModelResource._query_filter_other_logic(model, query, field, value)
            else:
                equal_filters.update({field: value})
        if equal_filters:
            query = query.filter_by(**equal_filters)
        if fields:
            query = query.with_entities(*[getattr(model, field) for field in fields])
        return query.all()
    
    @staticmethod
    def get_count_by_filters(model, fields=None, **filters):
        """get count by filters."""
        equal_filters = {}
        query = model.query
        if hasattr(model, "is_delete"):
            filters["is_delete"] = 0
        for field, value in filters.items():
            if isinstance(value, dict):
                query = _CommonModelResource._query_filter_other_logic(model, query, field, value)
            else:
                equal_filters.update({field: value})
        if equal_filters:
            query = query.filter_by(**equal_filters)
        if fields:
            query = query.with_entities(*[getattr(model, field) for field in fields])
        return query.count()

    def check_item_exist(self, check_fields: list=[], fields_dict: dict={}):
        """check item exist by fields."""
        if hasattr(self, "check_item_exist_func"):
            return self.check_item_exist_func(check_fields, fields_dict)
        if check_fields:
            query_filters = {
                field: fields_dict[field] for field in check_fields if field in fields_dict
            }
            return self.get_item_by_filters(self.model, **query_filters)
    
    def query_data_process(self, data):
        return query_data_process(
                    data,
                    date_format=self.date_format,
                    data_features=self.get_fields,
                    json_load_features=self.json_load_features,
                    json_dump_features=self.json_dump_features,
                )
    

class CommonListResource(_CommonModelResource):
    """
    list resource 部分封装, 方便拓展
    methods:
        1. get()  -> get list resource
        2. post() -> add item resource
    """
    def __init__(
        self,
        model=None,
        get_fields: Optional[Tuple[str, ...]] = None,
        date_format: int = 1,
        json_load_features: Optional[Tuple[str, ...]] = None,
        json_dump_features: Optional[Tuple[str, ...]] = None,
        get_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
        put_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
        post_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
        delete_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
        put_check_exist_fields: Optional[Tuple[str, ...]] = None,
        post_check_exist_fields: Optional[Tuple[str, ...]] = None,
    ):
        _CommonModelResource.__init__(
            self,
            model=model,
            get_fields=get_fields,
            date_format=date_format,
            json_load_features=json_load_features,
            json_dump_features=json_dump_features,
            get_parser_config=list(get_parser_config or []) + _GET_COMMON_PARAMS,
            put_parser_config=put_parser_config,
            post_parser_config=post_parser_config,
            delete_parser_config=delete_parser_config,
            put_check_exist_fields=put_check_exist_fields,
            post_check_exist_fields=post_check_exist_fields,
        )
        self.total = None

    @method_control
    def get(self):
        """
        get list resource common interface.
        """
        args = self.get_parser_args(self.get_parser_config)
        try:
            # step1: preprocess func.
            if hasattr(self, "get_preprocess_func"):
                args = self.get_preprocess_func(args)
                if isinstance(args, Response):
                    return args
            
            # step2: query data.
            items = self.get_items(args)

            # step3: postprocess func.
            if hasattr(self, "get_postprocess_func"):
                items = self.get_postprocess_func(items, args)

            # step4: data process.
            if hasattr(self, "get_query_data_process_func"):
                items = self.get_query_data_process_func(items, args)
                if isinstance(items, Response):
                    return items
            else:
                items = self.query_data_process(items)
            
            # step5: process return data.
            if hasattr(self, "get_process_return_data"):
                items = self.get_process_return_data(items, args)
                if isinstance(items, Response):
                    return items

        except Exception as e:
            ilog.error("db select error: %s" % traceback.format_exc())
            return self.http_resp(501, "数据库查询失败")
        
        return_data = {
            "total": self.total,
            "items": items,
        }    
        return self.http_resp(200, data=return_data)

    @method_control
    def post(self):
        """
        create item resource common interface.
        """
        args = self.get_parser_args(self.post_parser_config)
        if not args:
            return self.http_resp(404, "请求参数不能为空")
        try:
            # step1: check exist.
            if self.check_item_exist(self.post_check_exist_fields, args):
                return self.http_resp(400, "该数据已存在")
            
            # step2: preprocess func.
            if hasattr(self, 'post_preprocess_func'):
                args = self.post_preprocess_func(args)
                if isinstance(args, Response):
                    db.session.rollback()
                    return args
            
            # step3: create new item.
            new_item = self.model(
                **{key: args[key] for key in args if hasattr(self.model, key)}
            )
            db.session.add(new_item)
            db.session.flush()
            
            # step4: postprocess func.
            if hasattr(self, "post_postprocess_func"):
                new_item = self.post_postprocess_func(new_item, args)
                if isinstance(new_item, Response):
                    db.session.rollback()
                    return new_item
            
            # step5: data process.
            if hasattr(self, "post_query_data_process_func"):
                new_item = self.post_query_data_process_func(new_item, args)
                if isinstance(new_item, Response):
                    db.session.rollback()
                    return new_item
            else:
                new_item = self.query_data_process(new_item)
            
            # step6: process return data.
            if hasattr(self, "post_process_return_data"):
                new_item = self.post_process_return_data(new_item, args)
                if isinstance(new_item, Response):
                    db.session.rollback()
                    return new_item

            # step7: db commit.
            db.session.commit()
        
        except Exception as e:
            db.session.rollback()
            ilog.error("create item error: %s" % traceback.format_exc())
            return self.http_resp(404, "添加失败")
        
        return_data = {
            "item": new_item,
        }
        return self.http_resp(200, "添加成功", data=return_data)
    
    def get_items(self, args: dict):
        query = self.get_query(args)
        return query.all()

    def get_query(self, args: dict):
        if hasattr(self, "get_query_func"):
            query = self.get_query_func(args)
        else:
            query = db.session.query(self.model)
        if hasattr(self.model, "is_delete"):
            query = query.filter(self.model.is_delete == 0)
        # filter
        if hasattr(self, "add_query_filter"):
            query = self.add_query_filter(query, args)
        # total
        self.total = self.get_total(query)
        # sort
        if hasattr(self, 'add_query_sort'):
            query = self.add_query_sort(query, args)
        else:
            if hasattr(self.model, "create_time"):
                query = query.order_by(desc(self.model.create_time))
        # pagination
        if 'start' in args and 'number' in args:
            query = query.offset(args['start']).limit(args['number'])
        elif 'page' in args and 'per_page' in args:
            query = query.offset(args['per_page'] * (args['page'] - 1)).limit(args['per_page'])
        return query

    def get_total(self, query: Query):
        return query.count()


class CommonItemResource(_CommonModelResource):
    """
    item resource 部分封装, 方便拓展
    methods:
        1. get(id)    -> get item resource
        2. put(id)    -> put item resource
        3. delete(id) -> del item resource
    """
    def __init__(self,
            model=None,
            get_fields: Optional[Tuple[str, ...]] = None,
            date_format: int = 1,
            json_load_features: Optional[Tuple[str, ...]] = None,
            json_dump_features: Optional[Tuple[str, ...]] = None,
            get_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
            put_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
            post_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
            delete_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
            put_check_exist_fields: Optional[Tuple[str, ...]] = None,
            post_check_exist_fields: Optional[Tuple[str, ...]] = None,
        ):
        _CommonModelResource.__init__(self,
            model=model,
            get_fields=get_fields,
            date_format=date_format,
            json_load_features=json_load_features,
            json_dump_features=json_dump_features,
            get_parser_config=get_parser_config,
            put_parser_config=put_parser_config,
            post_parser_config=post_parser_config,
            delete_parser_config=delete_parser_config,
            put_check_exist_fields=put_check_exist_fields,
            post_check_exist_fields=post_check_exist_fields,
        )

    @method_control
    def get(self, id):
        """
        get item resource common interface by 'id'.
        """
        args = self.get_parser_args(self.get_parser_config)
        try:
            # step1: preprocess func.
            if hasattr(self, "get_preprocess_func"):
                args = self.get_preprocess_func(args)
                if isinstance(args, Response):
                    return args

            # step2: get item.
            if hasattr(self, "get_item_by_join_func"):
                item = self.get_item_by_join_func(id, args)
            else:
                item = self.get_item(id, args)
            if isinstance(item, Response):
                return item
            if item is None:
                return self.http_resp(404, "未查询到该数据")

            # step3: postprocess func.
            if hasattr(self, "get_postprocess_func"):
                item = self.get_postprocess_func(item, args)
                if isinstance(item, Response):
                    return item

            # step4: query data process.
            if hasattr(self, "get_query_data_process_func"):
                item = self.get_query_data_process_func(item, args)
                if isinstance(item, Response):
                    return item
            else:
                item = self.query_data_process(item)
            
            # step5: process return data.
            if hasattr(self, "get_process_return_data"):
                item = self.get_process_return_data(item, args)
                if isinstance(item, Response):
                    return item

        except Exception as e:
            ilog.error("db select error: %s" % traceback.format_exc())
            return self.http_resp(501, "数据库查询失败")

        return_data = {
            "key": id,
            "item": item,
        }
        return self.http_resp(200, data=return_data)
    
    @method_control
    def put(self, id):
        """
        update item resource common interface by 'id'.
        """
        args = self.get_parser_args(self.put_parser_config)
        if not args:
            return self.http_resp(404, "请求参数不能为空")
        try:
            # step1: get item.
            item = self.get_item(id, args)
            if isinstance(item, Response):
                db.session.rollback()
                return item
            if item is None:
                return self.http_resp(404, "未查询到该数据")
            
            # step2: preprocess func.
            if hasattr(self, "put_preprocess_func"):
                args = self.put_preprocess_func(item, args)
                if isinstance(args, Response):
                    db.session.rollback()
                    return args

            # step3: check fields exist.
            exist_item = self.check_item_exist(self.put_check_exist_fields, args)
            if exist_item and exist_item.id != item.id:
                return self.http_resp(status_code=400, message="存在相同记录,无法修改")
            
            # step4: update item.
            for key, value in args.items():
                # if value is not None and hasattr(item, key):
                if hasattr(item, key):
                    setattr(item, key, value)
            
            # step5: postprocess func.
            if hasattr(self, "put_postprocess_func"):
                item = self.put_postprocess_func(item, args)
                if isinstance(item, Response):
                    db.session.rollback()
                    return item

            # step6: query data process.
            if hasattr(self, "put_query_data_process_func"):
                item = self.put_query_data_process_func(item, args)
                if isinstance(item, Response):
                    db.session.rollback()
                    return item
            else:
                item = self.query_data_process(item)
            
            # step7: process return data.
            if hasattr(self, "put_process_return_data"):
                item = self.put_process_return_data(item, args)
                if isinstance(item, Response):
                    db.session.rollback()
                    return item

            # step8: db commit.
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            ilog.error("update item error: %s" % traceback.format_exc())
            return self.http_resp(505, "该数据修改失败")
        
        return_data = {
            "key": id,
            "item": item,
        }
        return self.http_resp(200, "该数据修改成功", data=return_data)
    
    @method_control
    def delete(self, id):
        """
        delete item resource common interface by 'id'.
        """
        args = self.get_parser_args(self.delete_parser_config)
        try:
            # step1: get item.
            item = self.get_item(id, args)
            if isinstance(item, Response):
                db.session.rollback()
                return item
            if item is None:
                return self.http_resp(404, "未查询到该数据")
            
            # step2: preprocess func.
            if hasattr(self, "delete_preprocess_func"):
                args = self.delete_preprocess_func(item, args)
                if isinstance(args, Response):
                    db.session.rollback()
                    return args
            
            # step3: delete item.
            if hasattr(item, "is_delete"):
                item.is_delete = 1
            else:
                db.session.delete(item)
            
            # step4: postprocess func.
            if hasattr(self, "delete_postprocess_func"):
                item = self.delete_postprocess_func(item, args)
                if isinstance(item, Response):
                    db.session.rollback()
                    return item

            # step5: db commit.
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            ilog.error("del item error: %s" % traceback.format_exc())
            return self.http_resp(506, "删除失败")
        
        return_data = {
            "key": id,
        }
        return self.http_resp(200, "删除成功", data=return_data)
    
    def get_item(self, id, args: dict):
        """
        get db item by 'id'.
        """
        if hasattr(self, 'get_item_func'):
            item = self.get_item_func(id, args)
        else:
            item = self.model.query.get(id)
        if getattr(item, "is_delete", 0):
            item = None
        return item 


# __all__ = ["ArgsConfig", "CommonResource"]
__all__ = ["ArgsConfig", "CommonResource", "CommonListResource", "CommonItemResource"]




