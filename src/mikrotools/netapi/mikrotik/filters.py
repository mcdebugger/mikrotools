VALID_OPS = ['=', '!=', '>', '>=', '<', '<=', '~', '!~'] # Mikrotik filter operators

class Filter:
    def __init__(self, *args):
        """
        Initialize a filter. The filter can be created in three ways:
        
        - By passing a single existing filter, which is copied.
        - By passing a field, operator and value as three arguments, for a single condition.
        - By passing a filter, operator and filter as three arguments, for combining filters.
        
        :param args: The arguments to create the filter with.
        :type args: tuple
        """
        self.conditions = []
        self._piped_operator = ''
        if len(args) == 3:
            if isinstance(args[0], Filter):
                # Combined filters
                self.conditions.append((args[1], args[0], args[2]))
            elif isinstance(args[0], str) and isinstance(args[1], str) and isinstance(args[2], str):
                # Single condition
                field, op, value = args
                if op not in VALID_OPS:
                    raise ValueError(f'Invalid operator: {op}. Valid operators: {", ".join(VALID_OPS)}')
                
                if not self.conditions:
                    self.conditions.append(('', field, op, value))
                else:
                    raise ValueError('Cannot instantiate a filter with multiple conditions.')
        elif len(args) == 1 and isinstance(args[0], Filter):
            # Copy existing filter
            self.conditions = args[0].conditions.copy()

    def and_(self, *vars) -> 'Filter':
        """
        Combine the current filter with the provided filters or conditions using the
        and operator.

        Args:
            *vars: A variable length argument list which can either contain a single
                filter or a three-element tuple representing a condition 
                (field, operator, value).

        Returns:
            Filter: A new filter instance with the combined conditions using the and operator.
        """
        return self._operator('and', *vars)
    
    def or_(self, *vars) -> 'Filter':
        """
        Combine the current filter with the provided filters or conditions using the
        or operator.

        Args:
            *vars: A variable length argument list which can either contain a single
                filter or a three-element tuple representing a condition 
                (field, operator, value).

        Returns:
            Filter: A new filter instance with the combined conditions using the or operator.
        """
        return self._operator('or', *vars)
    
    def _operator(self, operator: str, *vars) -> 'Filter':
        """
        Apply a logical operator to combine conditions or filters.

        This method either appends a filter or a condition to the current filter
        using the specified logical operator ('and' or 'or').

        Args:
            operator (str): The logical operator to apply ('and' or 'or').
            *vars: A variable length argument list which can either contain a single
                filter or a three-element tuple representing a condition 
                (field, operator, value).

        Returns:
            Filter: A new filter instance with the combined conditions.

        Raises:
            ValueError: If an invalid operator is provided in the condition.
        """
        new_filter = Filter(self)
        if len(vars) == 0:
            self._piped_operator = operator
            return self
        elif len(vars) == 1 and isinstance(vars[0], Filter):
            new_filter.conditions.append((operator, vars[0]))
            return new_filter
        elif len(vars) == 3:
            field, op, value = vars
            if op not in VALID_OPS:
                raise ValueError(f'Invalid operator: {op}. Valid operators: {", ".join(VALID_OPS)}')
            if not new_filter.conditions:
                new_filter.conditions.append(('', field, op, value))
            else:
                new_filter.conditions.append((operator, field, op, value))
            return new_filter
    
    def __add__(self, other: 'Filter') -> 'Filter':
        """
        Combine two filters. The conditions of the other filter are added to the conditions of this filter.
        The operator of the conditions of the other filter are used if present, otherwise 'and' is used.
        
        :param other: The filter to combine with this filter.
        :type other: Filter
        :return: A new filter with the combined conditions.
        :rtype: Filter
        """
        if isinstance(other, Filter):
            new_filter = Filter(self)
            for condition in other.conditions:
                operator, field, op, value = condition
                if operator:
                    new_filter.conditions.append((operator, field, op, value))
                else:
                    new_filter.conditions.append(('and', field, op, value))
            return new_filter
        else:
            raise ValueError('Invalid arguments for __add__(). Use Filter.')
    
    def __and__(self, other: 'Filter') -> 'Filter':
        """
        Combine two filters with the and operator.
        to_cli() will add parentheses for nested filters
        
        :param other: The filter to combine with this filter.
        :type other: Filter
        :return: A new filter with the combined filters.
        :rtype: Filter
        """
        if isinstance(other, Filter):
            return Filter(self, 'and', other)
        else:
            raise ValueError('Invalid arguments for __and__(). Use Filter.')
    
    def __or__(self, other: 'Filter') -> 'Filter':
        """
        Combine two filters with the or operator.
        to_cli() will add parentheses for nested filters

        :param other: The filter to combine with this filter.
        :type other: Filter
        :return: A new filter with the combined filters.
        :rtype: Filter
        :raises ValueError: If the argument is not a Filter.
        """
        if isinstance(other, Filter):
            return Filter(self, 'or', other)
        else:
            raise ValueError('Invalid arguments for __or__(). Use Filter.')
    
    # Comparison operators
    
    def eq(self, field: str, value: str) -> 'Filter':
        """
        Add an equality condition to the filter.

        :param field: The field to apply the condition to.
        :type field: str
        :param value: The value to compare the field with.
        :type value: str
        :return: This filter instance.
        :rtype: Filter
        """
        return self._add_condition(field, '=', value)
    
    def neq(self, field: str, value: str) -> 'Filter':
        """
        Add a not-equal condition to the filter.

        :param field: The field to apply the condition to.
        :type field: str
        :param value: The value to compare the field with.
        :type value: str
        :return: This filter instance.
        :rtype: Filter
        """
        return self._add_condition(field, '!=', value)
    
    def gt(self, field: str, value: str) -> 'Filter':
        """
        Add a greater-than condition to the filter.

        :param field: The field to apply the condition to.
        :type field: str
        :param value: The value to compare the field with.
        :type value: str
        :return: This filter instance.
        :rtype: Filter
        """
        return self._add_condition(field, '>', value)
    
    def lt(self, field: str, value: str) -> 'Filter':
        """
        Add a less-than condition to the filter.

        :param field: The field to apply the condition to.
        :type field: str
        :param value: The value to compare the field with.
        :type value: str
        :return: This filter instance.
        :rtype: Filter
        """
        return self._add_condition(field, '<', value)
    
    def gte(self, field: str, value: str) -> 'Filter':
        """
        Add a greater-than-or-equal condition to the filter.

        :param field: The field to apply the condition to.
        :type field: str
        :param value: The value to compare the field with.
        :type value: str
        :return: This filter instance.
        :rtype: Filter
        """
        return self._add_condition(field, '>=', value)
    
    def lte(self, field: str, value: str) -> 'Filter':
        """
        Add a less-than-or-equal condition to the filter.

        :param field: The field to apply the condition to.
        :type field: str
        :param value: The value to compare the field with.
        :type value: str
        :return: This filter instance.
        :rtype: Filter
        """
        return self._add_condition(field, '<=', value)
    
    def startswith(self, field: str, value: str) -> 'Filter':
        """
        Add a starts-with condition to the filter.

        :param field: The field to apply the condition to.
        :type field: str
        :param value: The value to compare the field with.
        :type value: str
        :return: This filter instance.
        :rtype: Filter
        """
        return self._add_condition(field, '~', value)
    
    def notstartswith(self, field: str, value: str) -> 'Filter':
        """
        Add a not-starts-with condition to the filter.

        :param field: The field to apply the condition to.
        :type field: str
        :param value: The value to compare the field with.
        :type value: str
        :return: This filter instance.
        :rtype: Filter
        """
        return self._add_condition(field, '!~', value)
    
    def _add_condition(self, field: str, op: str, value: str) -> 'Filter':
        """
        Add a condition to the filter.
        If preceeded by a piped operator, the condition is added as a piped condition.

        :param field: The field to apply the condition to.
        :type field: str
        :param op: The operator to use for the condition.
        :type op: str
        :param value: The value to compare the field with.
        :type value: str
        :return: This filter instance.
        :rtype: Filter
        """
        if self._piped_operator:
            # Piped condition
            self.conditions.append((self._piped_operator, field, op, value))
        elif self.conditions:
            # Combined condition
            self.conditions.append(('and', field, op, value))
        else:
            # Single condition
            self.conditions.append(('', field, op, value))
        
        self._piped_operator = ''
        return self
    
    def to_cli(self):
        """
        Convert the filter conditions into a CLI-compatible string representation.

        This method iterates over the filter's conditions and constructs a string 
        that represents the filter's logic in a format suitable for CLI usage, 
        adhering to Mikrotik filter syntax.

        The conditions can either be:
        - Single filters: represented by a filter object.
        - Combined filters: represented by two filter objects and an operator.
        - Single conditions: represented by a field, operator, and value.

        Returns:
            str: A string that represents the filter's conditions in a CLI-compatible 
            format, with conditions properly combined by the corresponding logical 
            operators.
        """
        if not self.conditions:
            raise ValueError('Filter is empty')
        parts = []
        for cond in self.conditions:
            if len(cond) == 2 and isinstance(cond[1], Filter):
                # Single filter
                operator, filter = cond
                clause = filter.to_cli()
                if operator:
                    clause = f'{operator} {clause}'
                parts.append(clause)
            if len(cond) == 3 and isinstance(cond[1], Filter) and isinstance(cond[2], Filter):
                # Combined filters
                operator, filter1, filter2 = cond
                part1 = filter1.to_cli()
                part2 = filter2.to_cli()
                if not part1 or not part2:
                    # Skip empty filters to avoid "()"
                    continue
                clause = f'({part1}) {operator} ({part2})'
                parts.append(clause)
            elif len(cond) == 4 and isinstance(cond[1], str) and isinstance(cond[2], str) and isinstance(cond[3], str):
                # Single condition
                operator, field, op, value = cond
                clause = f'{field}{op}"{value}"'
                if operator:
                    clause = f'{operator} {clause}'
                parts.append(clause)
        
        return ' '.join(parts)
