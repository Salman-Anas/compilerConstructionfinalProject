program lexicalEdge ;
begin
    { Testing extreme whitespace and newlines }
    
    varOne       :=          1000 ;
    
    { 
      This is a 
      multi-line comment 
      to ensure the lexer completely 
      ignores this entire block. 
    }
    
    varTwo := varOne + 
              2000 * ( 5 + 5 ) ;
              
    varThree := 
    varOne 
    + 
    varTwo
end .