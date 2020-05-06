# Data used in generation

view_dot_java = '''
import com.pengrad.telegrambot.TelegramBot;
import com.pengrad.telegrambot.model.Update;

public abstract class View {
    private String identifier;

    public View(String identifier) {
        this.identifier = identifier;
    }

    public String getIdentifier() {
        return identifier;
    }

    public abstract String handle(TelegramBot bot, Update update);
}
'''

handler_imports_dot_txt = '''
import com.pengrad.telegrambot.TelegramBot;
import com.pengrad.telegrambot.model.Update;

import database.Database;
import database.Event;
import records.State;

import java.io.IOException;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;


'''

imports_dot_txt = '''
import com.pengrad.telegrambot.TelegramBot;
import com.pengrad.telegrambot.model.Update;
import com.pengrad.telegrambot.model.request.ReplyKeyboardRemove;
import com.pengrad.telegrambot.model.request.ParseMode;
import com.pengrad.telegrambot.request.SendMessage;
import com.pengrad.telegrambot.request.SendDocument;import com.pengrad.telegrambot.request.SendMessage;
import com.pengrad.telegrambot.request.SendPhoto;import database.Database;

import database.Event;
import database.EventList;
import database.Date;
import java.util.ArrayList;
import java.util.Objects;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.file.Paths;

'''