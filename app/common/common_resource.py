import traceback
from typing import Optional, Tuple, Union
from typing import Dict, List, Any

from flask import g
from flask import abort
from flask import Response
from flask_restful import Resource
from flask_restful import reqparse
from sqlalchemy import desc
from sqlalchemy.orm.query import Query

from app import db, session
from app.common.log import ilog
from app.common.args_conf import ArgsConfig
from app.common.common_func import *
from app.common.interface_control import *
from app.common.constants import SUCCESS_CODE, FAILED_CODE


class CommonResource(Resource):
    """
    Base class for RESTful resources with unified request parsing and response formatting.

    Attributes:
        request_id (str): Unique ID for the request for tracing.
        get_parser_config (tuple): Argument configs for GET.
        put_parser_config (tuple): Argument configs for PUT.
        post_parser_config (tuple): Argument configs for POST.
        delete_parser_config (tuple): Argument configs for DELETE.
    """

    ALLOW_METHOD = dict()

    def __init__(
            self,
            get_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
            put_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
            post_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
            delete_parser_config: Optional[Tuple[ArgsConfig, ...]] = None,
    ):
        """
        Initialize CommonResource with parser configurations for HTTP methods.

        Args:
            get_parser_config (Optional[Tuple[ArgsConfig]]): GET method argument configs.
            put_parser_config (Optional[Tuple[ArgsConfig]]): PUT method argument configs.
            post_parser_config (Optional[Tuple[ArgsConfig]]): POST method argument configs.
            delete_parser_config (Optional[Tuple[ArgsConfig]]): DELETE method argument configs.
        """
        self.request_id = g.request_id
        self.get_parser_config = get_parser_config or []
        self.put_parser_config = put_parser_config or []
        self.post_parser_config = post_parser_config or []
        self.delete_parser_config = delete_parser_config or []

    def get(self, *args, **kwargs):
        """
        GET method handler. Defaults to 405 if not overridden.

        Returns:
            flask.Response: 405 Method Not Allowed.
        """
        abort(405)

    def put(self, *args, **kwargs):
        """
        PUT method handler. Defaults to 405 if not overridden.

        Returns:
            flask.Response: 405 Method Not Allowed.
        """
        abort(405)

    def post(self, *args, **kwargs):
        """
        POST method handler. Defaults to 405 if not overridden.

        Returns:
            flask.Response: 405 Method Not Allowed.
        """
        abort(405)

    def delete(self, *args, **kwargs):
        """
        DELETE method handler. Defaults to 405 if not overridden.

        Returns:
            flask.Response: 405 Method Not Allowed.
        """
        abort(405)

    @staticmethod
    def get_parser_args(configs: Tuple[ArgsConfig, ...]) -> Dict[str, Any]:
        """
        Parse arguments using flask_restful reqparse.

        Args:
            configs (Tuple[ArgsConfig, ...]): Tuple of ArgsConfig defining expected arguments.

        Returns:
            dict: Parsed and cleaned argument dict (excluding None values).
        """
        parser = reqparse.RequestParser()
        for config in configs:
            parser.add_argument(**config.to_dict())
        args = parser.parse_args()
        return {k: v for k, v in args.items() if v is not None}

    def http_resp(self, code: int = 1, message: str = "请求成功", data=None, *, status: int = 200) -> Response:
        """
        Unified HTTP response formatter.

        Args:
            code (int): Business code (1 for success, 0 for failure).
            message (str): Human-readable message.
            data (Any): Payload data to return.
            status (int): HTTP status code.

        Returns:
            flask.Response: JSON response with code/message/data/request_id.
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
    """
    A common resource handler for Flask-RESTful models, supporting
    basic CRUD helpers, filtering, and data serialization.
    """

    ALLOW_METHOD = dict()

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
        """
        Initialize a model-based resource.

        Args:
            model: SQLAlchemy model class for query operations.
            get_fields (Optional[Tuple[str]]): Fields to include in serialized output.
            date_format (int): 0 for '%Y-%m-%d', 1 for '%Y-%m-%d %H:%M:%S'.
            json_load_features (Optional[Tuple[str]]): Fields to JSON-deserialize.
            json_dump_features (Optional[Tuple[str]]): Fields to JSON-serialize.
            get_parser_config (Optional[Tuple[ArgsConfig]]): GET request parser config.
            put_parser_config (Optional[Tuple[ArgsConfig]]): PUT request parser config.
            post_parser_config (Optional[Tuple[ArgsConfig]]): POST request parser config.
            delete_parser_config (Optional[Tuple[ArgsConfig]]): DELETE request parser config.
            put_check_exist_fields (Optional[Tuple[str]]): Fields to check for uniqueness on PUT.
            post_check_exist_fields (Optional[Tuple[str]]): Fields to check for uniqueness on POST.
        """
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
    def get_item_by_pid(model, pid) -> Any:
        """
        Get a single item by primary ID (PID), ignoring deleted items.

        Args:
            model: SQLAlchemy model class.
            pid: Primary key ID.

        Returns:
            SQLAlchemy instance or None.
        """
        item = model.query.get(pid) if pid else None
        if getattr(item, "is_delete", 0):
            item = None
        return item

    @staticmethod
    def _query_filter_other_logic(model, query: Query, field: str, logic_value: dict) -> Query:
        """
        Apply advanced logic filtering to a SQLAlchemy query.

        Args:
            model: SQLAlchemy model class.
            query (Query): SQLAlchemy query.
            field (str): Field name.
            logic_value (dict): Logic condition, e.g. {"gt": 10}.

        Returns:
            Query: Updated SQLAlchemy query.
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
    def get_item_by_filters(model, fields=None, **filters) -> Any:
        """
        Get a single item by filters.

        Args:
            model: SQLAlchemy model class.
            fields (Optional[List[str]]): Fields to select.
            filters (dict): Filter conditions, may include logic dicts.

        Returns:
            SQLAlchemy instance or None.
        """
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
    def get_items_by_filters(model, fields=None, **filters) -> List[Any]:
        """
        Get multiple items by filters.

        Args:
            model: SQLAlchemy model class.
            fields (Optional[List[str]]): Fields to select.
            filters (dict): Filter conditions.

        Returns:
            List[Any]: List of SQLAlchemy model instances.
        """
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
    def get_count_by_filters(model, fields=None, **filters) -> int:
        """
        Count items by filters.

        Args:
            model: SQLAlchemy model class.
            fields (Optional[List[str]]): Fields to select (usually unused).
            filters (dict): Filter conditions.

        Returns:
            int: Count of items.
        """
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

    def check_item_exist(self, check_fields: list = [], fields_dict: dict = {}) -> Any:
        """
        Check whether an item exists based on specific fields.

        Args:
            check_fields (list): List of field names to check.
            fields_dict (dict): Dictionary of field values.

        Returns:
            SQLAlchemy instance or None: Matching instance if exists.
        """
        if check_fields:
            if hasattr(self, "check_item_exist_func"):
                return self.check_item_exist_func(check_fields, fields_dict)
        else:
            query_filters = {
                field: fields_dict[field] for field in check_fields if field in fields_dict
            }
            return self.get_item_by_filters(self.model, **query_filters)

    def query_data_process(self, data) -> Union[Dict, List]:
        """
        Format and process query result into serializable dict format.

        Args:
            data (Any): Model instance or list of instances.

        Returns:
            dict or list: Serialized JSON-compatible dict(s).
        """
        return query_data_process(
            data,
            date_format=self.date_format,
            data_features=self.get_fields,
            json_load_features=self.json_load_features,
            json_dump_features=self.json_dump_features,
        )


class CommonListResource(_CommonModelResource):
    """
    Common list resource base class, used for simplifying and standardizing 
    GET (list) and POST (create) resource interfaces.

    Methods:
        1. get()  -> Retrieve a list of items from the database.
        2. post() -> Create a new item in the database.
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
        """
        Initializes the resource with optional configurations for 
        parsing, field selection, and existence checks.
        """
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
        self.total = None  # Used to store total count of items for pagination

    @method_control
    @access_logger
    def get(self):
        """
        Handles GET requests to retrieve a list of items from the database.
        Applies optional preprocessing, filtering, sorting, pagination, 
        and post-processing.
        """
        args = self.get_parser_args(self.get_parser_config)
        try:
            # Step 1: Preprocess func
            if hasattr(self, "get_preprocess_func"):
                args = self.get_preprocess_func(args)
                if isinstance(args, Response):
                    return args

            # Step 2: Query data from database
            items = self.get_items(args)

            # Step 3: Postprocess func
            if hasattr(self, "get_postprocess_func"):
                items = self.get_postprocess_func(items, args)

            # Step 4: Custom or default data transformation
            if hasattr(self, "get_query_data_process_func"):
                items = self.get_query_data_process_func(items, args)
                if isinstance(items, Response):
                    return items
            else:
                items = self.query_data_process(items)

            # Step 5: Optional custom response data formatting
            if hasattr(self, "get_process_return_data"):
                items = self.get_process_return_data(items, args)
                if isinstance(items, Response):
                    return items

        except Exception as e:
            ilog.error("db select error: %s" % traceback.format_exc())
            return self.http_resp(FAILED_CODE, "查询失败")

        return_data = {
            "total": self.total,
            "items": items,
        }
        return self.http_resp(SUCCESS_CODE, data=return_data)

    @method_control
    @access_logger
    def post(self):
        """
        Handles POST requests to create a new item.
        Includes validations, existence checks, and rollback on failure.
        """
        args = self.get_parser_args(self.post_parser_config)
        if not args:
            return self.http_resp(FAILED_CODE, "参数不能为空")

        try:
            # Step 1: Check for existing item to avoid duplicates
            if self.check_item_exist(self.post_check_exist_fields, args):
                return self.http_resp(FAILED_CODE, "数据已存在")

            # Step 2: Preprocess request data before model creation
            if hasattr(self, 'post_preprocess_func'):
                args = self.post_preprocess_func(args)
                if isinstance(args, Response):
                    db.session.rollback()
                    return args

            # Step 3: Create and insert new item into database
            new_item = self.model(
                **{key: args[key] for key in args if hasattr(self.model, key)}
            )
            db.session.add(new_item)
            db.session.flush()

            # Step 4: Optional post-processing of newly created item
            if hasattr(self, "post_postprocess_func"):
                new_item = self.post_postprocess_func(new_item, args)
                if isinstance(new_item, Response):
                    db.session.rollback()
                    return new_item

            # Step 5: Optional custom processing of response data
            if hasattr(self, "post_query_data_process_func"):
                new_item = self.post_query_data_process_func(new_item, args)
                if isinstance(new_item, Response):
                    db.session.rollback()
                    return new_item
            else:
                new_item = self.query_data_process(new_item)

            # Step 6: Final formatting of return data
            if hasattr(self, "post_process_return_data"):
                new_item = self.post_process_return_data(new_item, args)
                if isinstance(new_item, Response):
                    db.session.rollback()
                    return new_item

            # Step 7: Commit transaction to DB
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            ilog.error("create item error: %s" % traceback.format_exc())
            return self.http_resp(FAILED_CODE, "添加失败")

        return_data = {
            "item": new_item,
        }
        return self.http_resp(SUCCESS_CODE, "添加成功", data=return_data)

    def get_items(self, args: dict) -> List[Any]:
        """
        Retrieve all items based on the given query arguments.
        """
        query = self.get_query(args)
        return query.all()

    def get_query(self, args: dict) -> Query:
        """
        Builds a query with optional filters, sorting, and pagination support.
        """
        # Use custom query function if defined
        if hasattr(self, "get_query_func"):
            query = self.get_query_func(args)
        else:
            query = db.session.query(self.model)

        # Filter out soft-deleted items if applicable
        if hasattr(self.model, "is_delete"):
            query = query.filter(self.model.is_delete == 0)

        # Apply additional filters
        if hasattr(self, "add_query_filter"):
            query = self.add_query_filter(query, args)

        # Compute total count for pagination
        self.total = self.get_total(query)

        # Apply sorting logic
        if hasattr(self, 'add_query_sort'):
            query = self.add_query_sort(query, args)
        else:
            if hasattr(self.model, "create_time"):
                query = query.order_by(desc(self.model.create_time))

        # Apply pagination (start/number or page/per_page)
        if 'start' in args and 'number' in args:
            query = query.offset(args['start']).limit(args['number'])
        elif 'page' in args and 'per_page' in args:
            query = query.offset(args['per_page'] * (args['page'] - 1)).limit(args['per_page'])

        return query

    def get_total(self, query: Query) -> int:
        """
        Returns the total number of records for the given query.
        """
        return query.count()


class CommonItemResource(_CommonModelResource):
    """
    Common item resource base class, used for simplifying and standardizing 
    GET (single item retrieval), PUT (update), and DELETE (remove) resource interfaces.

    Methods:
        1. get(id)    -> Retrieve a single item by its ID from the database.
        2. put(id)    -> Update an existing item by its ID in the database.
        3. delete(id) -> Delete an item by its ID from the database.
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
        """
        Initializes the resource with optional configurations for 
        parsing, field selection, and existence checks.
        """
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
    @access_logger
    def get(self, id):
        """
        Common interface to retrieve a single item resource by ID.
        """
        args = self.get_parser_args(self.get_parser_config)
        try:
            # Step1: preprocess func
            if hasattr(self, "get_preprocess_func"):
                args = self.get_preprocess_func(args)
                if isinstance(args, Response):
                    return args

            # Step2: Get item (optionally with joins)
            if hasattr(self, "get_item_by_join_func"):
                item = self.get_item_by_join_func(id, args)
            else:
                item = self.get_item(id, args)

            if isinstance(item, Response):
                return item
            if item is None:
                return self.http_resp(FAILED_CODE, "数据不存在")

            # Step3: Postprocess func
            if hasattr(self, "get_postprocess_func"):
                item = self.get_postprocess_func(item, args)
                if isinstance(item, Response):
                    return item

            # Step4: Optional data transformation
            if hasattr(self, "get_query_data_process_func"):
                item = self.get_query_data_process_func(item, args)
                if isinstance(item, Response):
                    return item
            else:
                item = self.query_data_process(item)

            # Step5: Final data formatting
            if hasattr(self, "get_process_return_data"):
                item = self.get_process_return_data(item, args)
                if isinstance(item, Response):
                    return item

        except Exception as e:
            ilog.error("db select error: %s" % traceback.format_exc())
            return self.http_resp(FAILED_CODE, "查询失败")

        return_data = {
            "key": id,
            "item": item,
        }
        return self.http_resp(SUCCESS_CODE, data=return_data)

    @method_control
    @access_logger
    def put(self, id):
        """
        Common interface to update a single item resource by ID.
        """
        args = self.get_parser_args(self.put_parser_config)
        if not args:
            return self.http_resp(FAILED_CODE, "参数不能为空")
        
        try:
            # Step1: Retrieve item
            item = self.get_item(id, args)
            if isinstance(item, Response):
                db.session.rollback()
                return item
            if item is None:
                return self.http_resp(FAILED_CODE, "数据不存在")

            # Step2: Preprocessing hook before update
            if hasattr(self, "put_preprocess_func"):
                args = self.put_preprocess_func(item, args)
                if isinstance(args, Response):
                    db.session.rollback()
                    return args

            # Step3: Check for duplicate record
            exist_item = self.check_item_exist(self.put_check_exist_fields, args)
            if exist_item and exist_item.id != item.id:
                return self.http_resp(FAILED_CODE, "存在相同记录")

            # Step4: Update fields
            for key, value in args.items():
                if hasattr(item, key):
                    setattr(item, key, value)

            # Step6: Postprocessing hook after update
            if hasattr(self, "put_postprocess_func"):
                item = self.put_postprocess_func(item, args)
                if isinstance(item, Response):
                    db.session.rollback()
                    return item

            # Step6: Optional data transformation
            if hasattr(self, "put_query_data_process_func"):
                item = self.put_query_data_process_func(item, args)
                if isinstance(item, Response):
                    db.session.rollback()
                    return item
            else:
                item = self.query_data_process(item)

            # Step7: Final data formatting hook
            if hasattr(self, "put_process_return_data"):
                item = self.put_process_return_data(item, args)
                if isinstance(item, Response):
                    db.session.rollback()
                    return item

            # Step8: Commit the update to DB
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            ilog.error("update item error: %s" % traceback.format_exc())
            return self.http_resp(FAILED_CODE, "修改失败")
        
        return_data = {
            "key": id,
            "item": item,
        }
        return self.http_resp(SUCCESS_CODE, "修改成功", data=return_data)

    @method_control
    @access_logger
    def delete(self, id):
        """
        Common interface to delete a single item resource by ID.
        """
        args = self.get_parser_args(self.delete_parser_config)
        try:
            # Step1: Retrieve item
            item = self.get_item(id, args)
            if isinstance(item, Response):
                db.session.rollback()
                return item
            if item is None:
                return self.http_resp(FAILED_CODE, "数据不存在")

            # Step2: Preprocessing hook befor item delete
            if hasattr(self, "delete_preprocess_func"):
                args = self.delete_preprocess_func(item, args)
                if isinstance(args, Response):
                    db.session.rollback()
                    return args

            # Step3: Soft delete if possible
            if hasattr(item, "is_delete"):
                item.is_delete = 1
            else:
                db.session.delete(item)

            # Step4: Postprocessing hook after item delete
            if hasattr(self, "delete_postprocess_func"):
                item = self.delete_postprocess_func(item, args)
                if isinstance(item, Response):
                    db.session.rollback()
                    return item

            # Step5: Commit delete option
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            ilog.error("del item error: %s" % traceback.format_exc())
            return self.http_resp(FAILED_CODE, "删除失败")
        
        return_data = {
            "key": id,
        }
        return self.http_resp(SUCCESS_CODE, "删除成功", data=return_data)

    def get_item(self, id, args: dict) -> Any:
        """
        Retrieve a single item from the database by its primary key ID.
        Supports custom retrieval via `get_item_func`, and soft delete checking via `is_delete`.
        """
        if hasattr(self, 'get_item_func'):
            item = self.get_item_func(id, args)
        else:
            item = self.model.query.get(id)
        if getattr(item, "is_delete", 0):
            item = None
        return item


__all__ = ["ArgsConfig", "CommonResource", "CommonListResource", "CommonItemResource"]








