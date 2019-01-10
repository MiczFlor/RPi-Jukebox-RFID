<?php
$volumevalue = exec("/usr/bin/sudo ".realpath(getcwd().'/../scripts/')."/playout_controls.sh -c=getvolume");
//$volumevalue = 73.6;//debug
$volumevalueselect = round(($volumevalue/5))*5;
$volumevaluedisplay = round($volumevalue);
?>
	  <div class="col-xs-6">
		  <div class="c100 p<?php print $volumevaluedisplay; ?>">
			<span><?php print $volumevaluedisplay; ?>%</span>
			<div class="slice">
				<div class="bar"></div>
				<div class="fill"></div>
			</div>
		  </div> 
	  </div>
