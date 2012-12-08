CREATE TABLE dogs (
    dog_id SERIAL PRIMARY KEY,
    weight float,
    name varchar(128) NOT NULL,
    color varchar(128) NOT NULL,
    added_on timestamp without time zone NOT NULL DEFAULT now(),
    updated_on timestamp without time zone
);

CREATE OR REPLACE FUNCTION get_dog(id integer) 
RETURNS TABLE (dog_id integer, weight float, name varchar(128), color varchar(128)) AS $$
BEGIN
    RETURN QUERY SELECT d.dog_id, d.weight, d.name, d.color FROM dogs d WHERE d.dog_id=id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_dogs()
RETURNS TABLE (dog_id integer, weight float, name varchar(128), color varchar(128)) AS $$
BEGIN
    RETURN QUERY SELECT d.dog_id, d.weight, d.name, d.color FROM dogs d;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_dog(id integer, new_name varchar(128), new_color varchar(128))
RETURNS SETOF dogs AS $$
BEGIN
    RETURN QUERY 
    UPDATE dogs d 
    SET name=new_name, color=new_color, updated_on=now()
    WHERE dog_id=id
    RETURNING d.*;
END;
$$ LANGUAGE plpgsql;

INSERT INTO dogs (weight, name, color) VALUES (2, 'Arturo', 'White');
INSERT INTO dogs (weight, name, color) VALUES (5, 'Pluto', 'Black');
