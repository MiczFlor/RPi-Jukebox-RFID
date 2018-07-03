              <h4>Volume</h4>

		<div class="progress">
			<?php
			$volumevalue = exec("/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=getvolume");
			if ($volumevalue == 0) {
				print '<div class="progress-bar progress-bar-danger" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width:100%">';
    				print 'Muted (0%)';
			}
			else {
				print '<div class="progress-bar progress-bar-info" role="progressbar" aria-valuenow="'.$volumevalue.'" aria-valuemin="0" aria-valuemax="100" style="width:'.$volumevalue.'%">';
    				print $volumevalue.'%';
			}
			?>
  			</div>
		</div>

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
