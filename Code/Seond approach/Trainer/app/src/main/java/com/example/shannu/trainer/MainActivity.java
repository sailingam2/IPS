package com.example.shannu.trainer;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.net.wifi.ScanResult;
import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.preference.PreferenceActivity;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;

import com.loopj.android.http.*;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.UnsupportedEncodingException;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLEncoder;
import java.util.List;

import cz.msebera.android.httpclient.Header;



import java.util.List;

import static java.lang.Integer.parseInt;

public class MainActivity extends AppCompatActivity {

    private Button startButton;
    private WifiManager wifimanager;
    private EditText scanId;
    private EditText indexId;
    private EditText serverId;
    private ListView WifiAps;
    private WifiScanReceiver wifiReciever;
    private String FileName;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
                        .setAction("Action", null).show();
            }
        });

        startButton = (Button) findViewById(R.id.button);
        startButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                WiFiScan();
            }
        });

        scanId = (EditText) findViewById(R.id.scanId);
        indexId = (EditText) findViewById(R.id.indexId);
        serverId = (EditText) findViewById(R.id.serverId);

        WifiAps = (ListView) findViewById(R.id.listView);

        wifimanager = (WifiManager) getSystemService(Context.WIFI_SERVICE);


        wifiReciever = new WifiScanReceiver();

    }

    private void WiFiScan() {
        Log.d("Development", "Register Device");
        registerReceiver(wifiReciever, new IntentFilter(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION));
        wifimanager.startScan();
        Log.d("Development", "Started Scan");
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    public void GetText(String indexID, ScanResult scanResult, String scanID, String address) {
        // Get user defined values
        String macID = scanResult.BSSID.toString();
        String ssid = scanResult.SSID;
        Integer level = scanResult.level;
        RequestParams requestParams = new RequestParams();
        requestParams.put("indexID", indexID);
        requestParams.put("macID", macID);
        requestParams.put("ssid", ssid);
        requestParams.put("rssi_value", level);
        requestParams.put("scanID", scanID);

        Log.d("Development",address);

        InposyHttpClient.post(address, requestParams, new TextHttpResponseHandler() {

            @Override
            public void onFailure(int statusCode, Header[] headers, String responseString, Throwable throwable) {

                Log.d("Failure", statusCode + " RS" + responseString);
            }

            @Override
            public void onSuccess(int statusCode, Header[] headers, String responseString) {

                if (statusCode == 200) {
                    Log.d("Success", "Successful post" + responseString);
                }

            }
        });
    }


    private class WifiScanReceiver extends BroadcastReceiver {


        public void onReceive(Context c, Intent intent) {

            Log.d("Development", "Into Wifi Results Available");

            // get the WiFi APs from WifiManager
            List<ScanResult> wifiResults = wifimanager.getScanResults();
            String[] wifis = new String[wifiResults.size()];


            // Send data to Server
            for (int i = 0; i < wifiResults.size(); i++) {
                Log.d("Success", wifiResults.get(i).SSID.toString());
                GetText(indexId.getText().toString(), wifiResults.get(i), scanId.getText().toString(), serverId.getText().toString() + "getTrainingScans");
                wifis[i] = indexId.getText().toString() + "," + scanId.getText().toString() + "," + wifiResults.get(i).SSID + "," + wifiResults.get(i).BSSID + "," + wifiResults.get(i).level + "\n";
            }

            scanId.setText(new Integer(parseInt(scanId.getText().toString()) + 1).toString());

            WifiAps.setAdapter(new ArrayAdapter<String>(c, android.R.layout.simple_list_item_1, wifis));
            unregisterReceiver(wifiReciever);
        }

    }
}

