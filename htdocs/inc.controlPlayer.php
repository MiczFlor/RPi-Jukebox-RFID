        <div class="btn-group controlPlayer" role="group" aria-label="player">
          <a href='?player=prev' class='btn btn-default btn-success'><i class='fa  fa-step-backward'></i></a>

<?php
    if (array_key_exists('status', $vlcStatus) && $vlcStatus['status'] === 'playing') {
        print '<a href="?player=pause" class="btn btn-default btn-success"><i class="fa fa-pause"></i></a>';
    }
    else {
        print '<a href="?player=play" class="btn btn-default btn-success"><i class="fa fa-play"></i></a>';
    }
?>
          <a href='?player=replay' class='btn btn-default btn-success'><i class='fa fa-refresh'></i></a>
<?php
    if (array_key_exists('status', $vlcStatus)) {
        print '<a href="?stop=true" class="btn btn-default btn-success"><i class="fa fa-stop"></i></a>';
    }
?>
          <a href='?player=next' class='btn btn-default btn-success'><i class='fa  fa-step-forward'></i></a>
        </div>