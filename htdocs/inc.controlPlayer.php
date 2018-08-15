        <div class="btn-group controlPlayer" role="group" aria-label="player" style="margin-bottom:0.5em;">
          <a href='?player=prev' class='btn btn-default btn-success btn-lg'><i class='fa  fa-step-backward'></i></a>

<?php
    if (array_key_exists('state', $playerStatus) && $playerStatus['state'] === 'play') {
        print '<a href="?player=pause" class="btn btn-default btn-success btn-lg"><i class="fa fa-pause"></i></a>';
    }
    else {
        print '<a href="?player=play" class="btn btn-default btn-success btn-lg"><i class="fa fa-play"></i></a>';
    }
?>
          <a href='?player=replay' class='btn btn-default btn-success btn-lg'><i class='fa fa-refresh'></i></a>
<?php
    if (array_key_exists('state', $playerStatus)) {
        print '<a href="?stop=true" class="btn btn-default btn-success btn-lg"><i class="fa fa-stop"></i></a>';
    }
?>
          <a href='?player=next' class='btn btn-default btn-success btn-lg'><i class='fa  fa-step-forward'></i></a>
<?php
    if ($playerStatus['repeat'] == "0") {
        print '<a href="?player=repeat" class="btn btn-default btn-warning btn-lg"><i class="fa fa-retweet"></i></a>';
    }
    elseif ($playerStatus['single'] == "1") {
        print '<a href="?player=repeatoff" class="btn btn-default btn-success btn-lg"><i class="fa fa-retweet"></i>1</a>';
    }
    else {
        print '<a href="?player=single" class="btn btn-default btn-success btn-lg"><i class="fa fa-retweet"></i></a>';
    }
?>
        </div>
