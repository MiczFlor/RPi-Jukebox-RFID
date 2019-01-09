<?php
/*
* eventually, the two pages cardEdit.php and cardRegisterNew.php should be one
* since most of the functionality is the same. This file is an intermediary step
* to unify both, taking some core functionality into one file and then see if it
* works for both.
*/

$messageAction = "";
$messageSuccess = "";

if($post['delete'] == "delete") {
    $messageAction .= "<p>The card with the ID '".$post['cardID']." has been deleted. 
        If you made a mistake, this is your chance to press 'Submit' to restore the card settings. 
        Else: Go <a href='index.php' class='mainMenu'><i class='mdi mdi-home'></i> Home</a>.</p>";
    // remove $fileshortcuts to cardID file in shortcuts
    $exec = "rm ".$fileshortcuts;
    if($debug == "true") {
        print "<pre>deleting shortcut:\n";
        print $exec;
        print "</pre>";
    } else {
        exec($exec);
    }
} elseif($post['submit'] == "submit") {
    /*
    * error check
    */
    // The dropdown menus for the audiofolders in the section "Audio folders" and "YouTube" are interchangeable.
    // So you may select the folder in any of both.
    // Check if two different audiofolders are selectied in the dropdowns
    if(isset($post['audiofolder']) && isset($post['YTaudiofolder'])) {
        //$messageAction .= $lang['cardRegisterErrorTooMuch']." (error 007)";
    } elseif(!isset($post['audiofolder']) && isset($post['YTaudiofolder'])) {
        //set the audiofolder variable (if unset) to the YTaudiofolder variable. This makes the further handling easier.
        $post['audiofolder'] = $post['YTaudiofolder'];
    }
    // Like above: stream folder inputs are interchangeable.
    // Check if two different stream folder names are entered
    if(isset($post['streamFolderName']) && isset($post['YTstreamFolderName']) && $post['streamFolderName'] != $post['YTstreamFolderName']) {
        $messageAction .= $lang['cardRegisterErrorTooMuch']." (error 008)";
    } elseif(!isset($post['streamFolderName']) && isset($post['YTstreamFolderName'])) {
        //set the streamFolderName variable (if unset) to the YTstreamFolderName variable. This makes the further handling easier.
        $post['streamFolderName'] = $post['YTstreamFolderName'];
    }

    // posted too much?
    if(isset($post['streamURL']) && isset($post['audiofolder'])) {
        $messageAction .= $lang['cardRegisterErrorStreamAndAudio']." (error 001)";
    }
    
    // posted too little?
    if((!isset($post['streamURL']) || !isset($post['streamType'])) && !isset($post['audiofolder']) && !isset($post['YTstreamURL'])) {
        $messageAction .= $lang['cardRegisterErrorStreamOrAudio']." (error 002)";
    }

    // posted streamFolderName and audiofolder
    if(isset($post['streamFolderName']) && isset($post['audiofolder'])) {
        $messageAction .= $lang['cardRegisterErrorExistingAndNew']." (error 003)";
    }
    
    // streamFolderName already exists
    if(isset($post['streamFolderName']) && file_exists($Audio_Folders_Path.'/'.$post['streamFolderName'])) {
        $messageAction .= $lang['cardRegisterErrorExistingFolder']." (error 004)";
    }
    
    // No streamFolderName entered
    if(isset($post['streamURL']) && !isset($post['streamFolderName'])) {
        $messageAction .= $lang['cardRegisterErrorSuggestFolder']." (error 005)";
        // suggest folder name: get rid of strange chars, prefixes and the like
        $post['streamFolderName'] = $link = str_replace(array('http://','https://','/','=','-','.', 'www','?','&'), '', $post['streamURL']);
    }
    
    // streamFolderName not given
    if( ( isset($post['streamURL']) || isset($post['YTstreamURL']) ) && !isset($post['audiofolder']) && !isset($post['streamFolderName'])) {
        $messageAction .= $lang['cardRegisterErrorSuggestFolder']." (error 006)";
        // suggest folder name: get rid of strange chars, prefixes and the like
        $post['streamFolderName'] = $link = str_replace(array('http://','https://','/','=','-','.', 'www','?','&'), '', $post['streamURL']);
    }
    
    /*
    * any errors?
    */
    if($messageAction == "") {
        /*
        * do what's asked of us
        */
        $fileshortcuts = $conf['shared_abs']."/shortcuts/".$post['cardID'];
        if(isset($post['streamURL'])) {
            /*
            * Stream URL to be created
            */
            include('inc.processAddNewStream.php');
            // success message
            $messageSuccess = "<p>".$lang['cardRegisterStream2Card']." ".$lang['globalFolder']." '".$post['streamFolderName']."' ".$lang['globalCardId']." '".$post['cardID']."'</p>";
        }
        elseif(isset($post['YTstreamURL'])) {
            /*
            * Stream URL to be created
            */
            include('inc.processAddYT.php');
            // success message
            $messageSuccess = $lang['cardRegisterDownloadingYT'];
        } else {
            /*
            * connect card with existing audio folder
            */
            // write $post['audiofolder'] to cardID file in shortcuts
            $exec = "rm ".$fileshortcuts."; echo '".$post['audiofolder']."' > ".$fileshortcuts."; chmod 777 ".$fileshortcuts;
            exec($exec);
            // success message
            $messageSuccess = "<p>".$lang['cardRegisterFolder2Card']."  ".$lang['globalFolder']." '".$post['audiofolder']."' ".$lang['globalCardId']." '".$post['cardID']."'</p>";
        }
    } else {
        /*
        * Warning given, action can not be taken
        */
    }
}
?>
