              <h4>Volume</h4>
        
                <form name='volume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
                  <select name='volume'>
                     <option value='0'>Mute (0%)</option>
                     <option value='30'>30%</option>
                     <option value='50'>50%</option>
                     <option value='75'>75%</option>
                     <option value='80'>80%</option>
                     <option value='85'>85%</option>
                     <option value='90'>90%</option>
                     <option value='95'>95%</option>
                     <option value='100'>100%</option>
                  </select>
                <input type='submit' name='submit' value='Set volume'/>
                </form>          
