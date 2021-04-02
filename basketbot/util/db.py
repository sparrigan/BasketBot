from marshmallow_sqlalchemy import ModelConversionError, SQLAlchemyAutoSchema, ModelSchema

def setup_schema(Base, session):
    """
    Automatically create schemas for all relations in Base. 
    This is run on an SQLAlchemy event trigger in basketbot.datamodel
    """
    def setup_schema_fn():
        for class_ in Base._decl_class_registry.values():
            if hasattr(class_, "__tablename__"):
                if class_.__name__.endswith("Schema"):
                    raise ModelConversionError(
                        "For safety, setup_schema can not be used when a"
                        "Model class ends with 'Schema'"
                    )

                class Meta(object):
                    model = class_
                    sqla_session = session

                schema_class_name = "%sSchema" % class_.__name__

                schema_class = type(
                    schema_class_name, (ModelSchema,), {"Meta": Meta}
                )

                setattr(class_, "Schema", schema_class)

    return setup_schema_fn


