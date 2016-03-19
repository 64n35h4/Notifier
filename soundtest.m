function knockNum = knock(filename)
%[yt,fst]=audioread('sound018.m4a');
%%clc;
%%clear all;
%%close all;

knockNum = 0;
[y,fs]=audioread(filename);
f_y=fft(y);
g_y=f_y(1:(length(f_y)/2));
f=length(g_y);
t=1:length(y);
t=t/fs;
f=1:f;
f = f/length(g_y); 
%%figure;
%%plot(t,y(:,1)); %TO FIX!! 20log()
%%axis([0 inf -1 1]);
s=max(max(abs(g_y)));
%%suptitle('Sound in time domain');
%%xlabel('time (Sec)');
%%ylabel('Amplitude( V ) ');
%figure;
%plot(f,abs(g_y));
%title('sound in freq domain');
%axis([0 0.3 0 2000]);
i=1;
while i<(length(y)-(fs/2))

    if(y(i,1)>0.1)
        yMaxH = max(y(i:i+round(0.04*fs),1));
        
        yMaxL = max(y(i+round(0.04*fs):i+round(0.06*fs),1));
        %yMaxHarr(j)=yMaxH;
        %yMaxLarr(j)=yMaxL;
        if ( ((yMaxL*100)/yMaxH) < 60)
            knockNum = knockNum + 1;
        end
        i = i + round(0.05*fs);
    else
        i = i + 1;
    end
    %j = j+1;
end
%%h = msgbox(sprintf('knock: %g' , knockNum),'Number of knocks','help');
end

