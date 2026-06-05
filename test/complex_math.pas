program complexMath ;
begin
    { Testing deep parentheses and operator precedence }
    baseValue := 10 ;
    multiplier := 20 ;
    offset := 5 ;
    
    calc1 := ( baseValue + multiplier ) * ( offset + ( 10 * 2 ) ) ;
    calc2 := calc1 + 100 * baseValue ;
    
    finalResult := ( calc1 * calc2 ) + ( 50 * ( 2 + 3 ) )
end .